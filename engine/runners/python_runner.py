import logging
import os
import resource  # Note: this is a UNIX-specific module.
import subprocess

from .abstract_runner import AbstractRunner

logger = logging.getLogger(__name__)


class PythonRunner(AbstractRunner):
    def run(self, code_filename, input_str):
        command = ['python3', code_filename]

        try:
            timeout_seconds = 1

            r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

            engine_venv = os.environ.copy()
            engine_venv["PATH"] = "/usr/sbin:/sbin:" + engine_venv["PATH"]
            process = subprocess.Popen(command, env=engine_venv, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate(input=bytes(input_str, encoding='utf-8'), timeout=timeout_seconds)

            r = resource.getrusage(resource.RUSAGE_CHILDREN)

            p_info = {
                'returnCode': process.returncode,
                'utime': r.ru_utime - r0.ru_utime,
                'stime': r.ru_stime - r0.ru_stime,
                'maxrss': r.ru_maxrss
            }
        except subprocess.CalledProcessError as ex:
            logger.critical("%s", ex)
            logger.critical("Program returned non-zero code %s", ex.returncode)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)
        except subprocess.TimeoutExpired as ex:
            logger.critical("%s", ex)
            logger.critical("Program took longer than %d seconds.", ex.timeout)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)

        output_str = stdout.decode('utf-8').strip()

        logger.debug("Finished running user code. Return code %d.", p_info['returnCode'])
        logger.debug("utime: %f, stime: %f", p_info['utime'], p_info['stime'])
        logger.debug("maxrss: %d kB", p_info['maxrss'])  # resource

        return output_str, p_info
