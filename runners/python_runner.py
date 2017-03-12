# python_runner.py

import abc
from runners.abstract_runner import AbstractRunner
import subprocess
import util


class PythonRunner(AbstractRunner):

    def run(self, code_filename, input_filename):
        command = ['python3', code_filename]

        # input_arguments = util.read_list_from_file(input_filename)
        input_arguments = input_filename

        for arg in input_arguments:
            command += str(arg)

        output_raw = subprocess.check_output(command)
        def conv(number): return float(number)
        output_list = output_raw.decode('utf-8').split(sep=' ')
        output_list = list(map(conv, output_list))

        return output_list
