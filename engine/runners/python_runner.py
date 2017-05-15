# python_runner.py

import abc
from subprocess import run, PIPE, CalledProcessError, TimeoutExpired

import util
from .abstract_runner import AbstractRunner


class PythonRunner(AbstractRunner):

    def run(self, code_filename, args_list=None, timeout=10):
        command = ['python3', code_filename] + args_list

        try:
            timeout_seconds = 1
            process = run(command, stdout=PIPE, timeout=timeout_seconds, check=True)
        except CalledProcessError as ex:
            print(ex)
            print("Program returned non-zero code", ex.returncode)
            print("Command used:", ' '.join(ex.cmd))
            print("Program output:", ex.stdout)
        except TimeoutExpired as ex:
            print(ex)
            print("Program took longer than", ex.timeout, "seconds.")
            print("Command used:", ' '.join(ex.cmd))
            print("Program output:", ex.stdout)

        output_str = process.stdout
        output_list = output_str.split()

        return output_list
