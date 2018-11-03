import logging
import pickle
import shutil
import fileinput

import engine.util as util
from .abstract_runner import AbstractRunner
from ..simple_lxd import simple_lxd as lxd

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


class PythonRunner(AbstractRunner):
    def run(self, container_name, code_filename, function_name, input_tuple):
        logger.debug("Running {:s} with input {:}".format(code_filename, input_tuple))

        run_id = code_filename.split('.')[0]
        input_pickle = '{}.input.pickle'.format(run_id)
        with open(input_pickle, mode='wb') as f:
            logger.debug("Pickling input tuple in {:s}...".format(input_pickle))
            pickle.dump(input_tuple, file=f)

        runner_file = "{}.run.py".format(run_id)
        shutil.copy("run_it.py", runner_file)

        # Replace "$FUNCTION_NAME" in run_it.py with function name to execute from
        # the problem module.
        logger.info("Replacing $FUNCTION_NAME->{:s} in {:s}...".format(function_name, runner_file))
        with fileinput.FileInput(runner_file, inplace=True) as f:
            for line in f:
                print(line.replace("$FUNCTION_NAME", function_name), end='')

        for file_name in [code_filename, runner_file, input_pickle]:
            source_path = file_name
            target_path = "/root/{}".format(file_name)
            _, push_retval, push_stdout = lxd.file_push(container_name, source_path, target_path)

            if push_retval != 0:
                raise FilePushError(push_stdout)

        runner_path = "/root/{}".format(runner_file)
        command = ['python3', runner_path]
        _, exec_retval, exec_stdout = lxd.execute(container_name, command)

        if exec_retval != 0:
            raise EngineExecutionError(exec_stdout)

        p_info = {
            'return_value': exec_retval,
            'stdout': exec_stdout,
            'runtime': 0,
            'max_mem_usage': 0
        }

        output_pickle = '{}.output.pickle'.format(run_id)
        source_path = '/root/{}'.format(output_pickle)
        target_path = output_pickle

        _, pull_retval, pull_stdout = lxd.file_pull(container_name, source_path, target_path)

        if pull_retval != 0:
            raise FilePullError(pull_stdout)

        with open(output_pickle, mode='rb') as f:
            output_dict = pickle.load(f)

        user_output = output_dict['user_output']
        p_info['runtime'] = output_dict['runtime']
        p_info['max_mem_usage'] = output_dict['max_mem_usage']

        logger.debug("Finished running user code.")
        logger.debug("runtime: {:g} s, max_mem_usage: {:g} kB".format(p_info['runtime'], p_info['max_mem_usage']))

        util.delete_file(input_pickle)
        util.delete_file(output_pickle)
        util.delete_file(runner_file)

        return user_output, p_info
