import fileinput
import json
import logging
import pickle
import shutil
import subprocess
from subprocess import CalledProcessError
from abc import ABCMeta, abstractmethod

import docker
import numpy as np

import engine.util as util
from engine.docker_util import docker_file_push, docker_file_pull, docker_execute


logger = logging.getLogger(__name__)


class FilePushError(Exception):
    def __init__(self, message):
        super().__init__(message)


class EngineExecutionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FilePullError(Exception):
    def __init__(self, message):
        super().__init__(message)


class AbstractRunner(metaclass=ABCMeta):
    @abstractmethod
    def run(self, container_name, filename, function_name, input_tuples, output_tuples):
        """Execute the given file using input_str as input through stdin and return the program's output."""


# In case we need to serialize a numpy.ndarray to JSON.
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class CodeRunner(AbstractRunner):
    def __init__(self, language):
        self.util_files = []
        self.file_type = "pickle"
        self.push_correct_output = False

        if language == "python":
            self.run_script_filename = "run_py.py"
        elif language == "javascript":
            self.run_script_filename = "run_js.py"
        elif language == "julia":
            self.run_script_filename = "run_jl.py"
            self.file_type = "json"
        elif language == "c":
            self.run_script_filename = "run_c.py"
            self.push_correct_output = True
        else:
            raise ValueError("CodeRunner does not support language={:}".format(language))

    def run(self, container_id, code_filename, function_name, input_tuples, correct_output_tuples):
        logger.info("Running {:s} with {:d} inputs...".format(code_filename, len(input_tuples)))

        run_id = code_filename.split(".")[0]

        # Pickle all the input tuples into one file.
        if self.file_type == "pickle":
            input_pickle = "{:s}.input.pickle".format(run_id)
            with open(input_pickle, mode="wb") as f:
                logger.debug("Pickling input tuples in {:s}...".format(input_pickle))
                pickle.dump(input_tuples, file=f, protocol=pickle.HIGHEST_PROTOCOL)
        elif self.file_type == "json":
            input_pickle = "{:s}.input.json".format(run_id)
            with open(input_pickle, mode="w") as f:
                logger.debug("Pickling input tuples in {:s}...".format(input_pickle))
                json.dump(input_tuples, f, cls=NumpyEncoder)

        # Copy the relevant boilerplate run script into the current working directory.
        runner_file = "{:s}.run.py".format(run_id)
        shutil.copy(self.run_script_filename, runner_file)

        # Replace "$FUNCTION_NAME" in the run script with the actual function name to call
        # (as defined in the problem module).
        logger.debug("Replacing $FUNCTION_NAME->{:s} in {:s}...".format(function_name, runner_file))
        with fileinput.FileInput(runner_file, inplace=True) as f:
            for line in f:
                print(line.replace("$FUNCTION_NAME", function_name), end="")

        # Push all the files we need into the Linux container.
        required_files = [code_filename, runner_file, input_pickle]
        if self.push_correct_output:
            correct_output_pickle = "{:s}.correct.pickle".format(run_id)
            with open(correct_output_pickle, mode="wb") as f:
                logger.debug(
                    "Pickling correct output tuples in {:s}...".format(correct_output_pickle)
                )
                pickle.dump(correct_output_tuples, file=f, protocol=pickle.HIGHEST_PROTOCOL)

            required_files.append(correct_output_pickle)

        for file_name in required_files + self.util_files:
            source_path = file_name
            target_path = "/root/{:s}".format(file_name)

            try:
                push_stdout = docker_file_push(container_id, source_path, target_path)
            except subprocess.CalledProcessError:
                # If pushing a file fails then declutter remaining files and raise an exception.
                for fn in required_files:
                    util.delete_file(fn)
                # TODO: push_stdout might not be set here, if the push process really fails
                raise FilePushError(push_stdout)

        # Tell the Linux container to execute the run script that will run the user's code.
        runner_path = "/root/{}".format(runner_file)
        command = ["python3", runner_path]

        logger.debug("Trying to execute function in docker...")
        try:
            exec_retval, exec_stdout = docker_execute(container_id, command)
        except docker.errors.APIError:
            # If we fail to connect through docker, clean up the files
            for fn in required_files:
                util.delete_file(fn)
            raise EngineExecutionError(exec_stdout)

        # Or if the code failed to run properly, clean up the files
        if exec_retval != 0:
            for fn in required_files:
                util.delete_file(fn)
            raise EngineExecutionError(exec_stdout)

        user_outputs = []
        process_infos = []

        # Read all the output that the user produced.
        # Each test case's output will end up it one output pickle file.
        for i, _ in enumerate(input_tuples):
            output_pickle = "{:s}.output{:d}.pickle".format(run_id, i)
            source_path = "/root/{:s}".format(output_pickle)
            target_path = output_pickle

            try:
                pull_stdout = docker_file_pull(container_id, source_path, target_path)
            except CalledProcessError:
                for fn in required_files:
                    util.delete_file(fn)
                raise FilePullError(pull_stdout)

            with open(output_pickle, mode="rb") as f:
                output_dict = pickle.load(f)

            # TODO: exec_retval will always be zero here, so why return it?
            p_info = {
                "return_value": exec_retval,
                "stdout": exec_stdout,
                "runtime": output_dict["runtime"],
                "max_mem_usage": output_dict["max_mem_usage"],
            }

            user_outputs.append(output_dict["user_output"])
            process_infos.append(p_info)

            logger.debug(
                "runtime: {:g} s, max_mem_usage: {:g} kB".format(
                    p_info["runtime"], p_info["max_mem_usage"]
                )
            )

            util.delete_file(output_pickle)

        logger.info("Finished running user code.")

        for fn in required_files:
            util.delete_file(fn)

        return user_outputs, process_infos
