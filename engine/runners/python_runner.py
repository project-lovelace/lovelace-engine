import resource  # Note: this is a UNIX-specific module.
from subprocess import run, Popen, PIPE, CalledProcessError, TimeoutExpired

import util
from .abstract_runner import AbstractRunner

import logging
logger = logging.getLogger(__name__)


class PythonRunner(AbstractRunner):
    def run(self, code_filename, input_str):
        command = ['python3', code_filename]

        try:
            timeout_seconds = 1
            r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
            process = Popen(command, stdin=PIPE, stdout=PIPE)
            stdout, stderr = process.communicate(input=bytes(input_str, encoding='utf-8'), timeout=timeout_seconds)
            r = resource.getrusage(resource.RUSAGE_CHILDREN)
        except CalledProcessError as ex:
            logger.critical("%s", ex)
            logger.critical("Program returned non-zero code %s", ex.returncode)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)
        except TimeoutExpired as ex:
            logger.critical("%s", ex)
            logger.critical("Program took longer than %d seconds.", ex.timeout)
            logger.critical("Command used: %s", ''.join(ex.cmd))
            logger.critical("Program output: %s", ex.stdout)

        output_str = stdout.decode('utf-8').strip()

        p_info = {
            'return_code': process.returncode,
            'utime': r.ru_utime - r0.ru_utime,
            'stime': r.ru_stime - r0.ru_stime,
            'maxrss': r.ru_maxrss
        }

        logger.debug("Finished running user code. Return code %d.", p_info['return_code'])
        logger.debug("utime: %f, stime: %f", p_info['utime'], p_info['stime'])
        logger.debug("maxrss: %d kB", p_info['maxrss'])

        return output_str, p_info
