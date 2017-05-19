import resource  # Note: this is a UNIX-specific module.
import psutil, subprocess

import util
from .abstract_runner import AbstractRunner

import logging
logger = logging.getLogger(__name__)


class PythonRunner(AbstractRunner):
    def run(self, code_filename, input_str):
        command = ['python3', code_filename]

        try:
            timeout_seconds = 1

            # TODO: Use psutil.rlimit to set CPU/RAM/etc. restrictions on the process.
            r0 = resource.getrusage(resource.RUSAGE_CHILDREN)

            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            # process = psutil.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate(input=bytes(input_str, encoding='utf-8'), timeout=timeout_seconds)

            r = resource.getrusage(resource.RUSAGE_CHILDREN)

            # Using resource
            p_info = {
                'return_code': process.returncode,
                'utime': r.ru_utime - r0.ru_utime,
                'stime': r.ru_stime - r0.ru_stime,
                'maxrss': r.ru_maxrss
            }

            # Using psutil
            # p_info = {
            #     'return_code': process.returncode,
            #     'utime': process.cpu_times().user,
            #     'stime': process.cpu_times().system,
            #     'rss': process.memory_info().rss
            # }
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

        logger.debug("Finished running user code. Return code %d.", p_info['return_code'])
        logger.debug("utime: %f, stime: %f", p_info['utime'], p_info['stime'])
        logger.debug("maxrss: %d kB", p_info['maxrss'])  # resource
        # logger.debug("rss: %d kB", p_info['rss'])  # psutil

        return output_str, p_info
