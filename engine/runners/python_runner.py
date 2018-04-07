import logging
import os
import pickle
import resource  # Note: this is a UNIX-specific module.
import shutil
import subprocess

from .abstract_runner import AbstractRunner
import engine.util as util
# from ..simple_lxd import simple_lxd as lxd


logger = logging.getLogger(__name__)


class PythonRunner(AbstractRunner):
    def run(self, code_filename, input_tuple):
        run_id = code_filename.split('.')[0]
        input_pickle = '{}.input.pickle'.format(run_id)
        with open(input_pickle, mode='wb') as f:
            pickle.dump(input_tuple, file=f)

        engine_venv = os.environ.copy()
        engine_venv["PATH"] = "/usr/sbin:/sbin:" + engine_venv["PATH"]

        runner_file = '{}.run.py'.format(run_id)
        shutil.copy('run_it.py', runner_file)

        command = ['python3', runner_file]
        timeout_seconds = 10
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

        try:
            process = subprocess.Popen(command, env=engine_venv)
            process.wait(timeout_seconds)
        except subprocess.CalledProcessError as ex:
            logger.critical("%s", ex)
            logger.critical("Program returned non-zero code %s", ex.returncode)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)
            return
        except subprocess.TimeoutExpired as ex:
            logger.critical("%s", ex)
            logger.critical("Program took longer than %d seconds.", ex.timeout)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)
            return

        r = resource.getrusage(resource.RUSAGE_CHILDREN)
        p_info = {
            'returnCode': process.returncode,
            'utime': r.ru_utime - r0.ru_utime,
            'stime': r.ru_stime - r0.ru_stime,
            'maxrss': r.ru_maxrss
        }

        output_pickle = '{}.output.pickle'.format(run_id)
        with open(output_pickle, mode='rb') as f:
            user_output = pickle.load(f)

        logger.debug("Finished running user code. Return code %d.", p_info['returnCode'])
        logger.debug("utime: %f, stime: %f", p_info['utime'], p_info['stime'])
        logger.debug("maxrss: %d kB", p_info['maxrss'])  # resource

        util.delete_file(input_pickle)
        util.delete_file(output_pickle)
        util.delete_file(runner_file)

        return user_output, p_info

    # container_name = str(hash(code_filename))
    # lxd.launch("images:ubuntu/xenial/i386", name=container_name)
    #
    # source_path = code_filename
    # target_path = "/tmp/{}".format(code_filename)
    # lxd.file_push(container_name, source_path, target_path)
    #
    # command = ['python3', target_path]
    # lxd.execute(container_name, command, mode="interactive")
