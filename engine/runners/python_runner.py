# python_runner.py

import abc
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
            process = Popen(command, stdin=PIPE, stdout=PIPE)
            stdout = process.communicate(input=bytes(input_str, encoding='utf-8'), timeout=timeout_seconds)[0]
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
        return output_str
