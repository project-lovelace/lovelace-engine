import os
import glob
import time
import json
import base64
import requests
import unittest


class TestApi(unittest.TestCase):
    solutions_dir = "/home/ada/lovelace/lovelace-solutions/"
    python_solutions_dir = os.path.join(solutions_dir, "python")
    javascript_solutions_dir = os.path.join(solutions_dir, "javascript")
    julia_solutions_dir = os.path.join(solutions_dir, "julia")
    c_solutions_dir = os.path.join(solutions_dir, "c")

    @staticmethod
    def submit_solution(file_path):
        with open(file_path, 'r') as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')

        problem_name, extension = os.path.basename(file_path).split(sep='.')
        language = {'py': "python", 'js': "javascript", 'jl': "julia", 'c': "c"}.get(extension)

        payload_dict = {
            'problem': problem_name,
            'language': language,
            'code': code_b64,
        }
        payload_json = json.dumps(payload_dict)

        response = requests.post('http://localhost:14714/submit', data=payload_json)
        response_data = json.loads(response.text)

        return response_data

    def test_all_problems_python_success(self):
        for relative_filepath in glob.glob(os.path.join(self.python_solutions_dir, "*.py")):
            absolute_filepath = os.path.join(self.python_solutions_dir, os.path.basename(relative_filepath))

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(result['success'], "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)))

    def test_all_problems_javascript_success(self):
        for relative_filepath in glob.glob(os.path.join(self.javascript_solutions_dir, "*.js")):
            absolute_filepath = os.path.join(self.javascript_solutions_dir, os.path.basename(relative_filepath))

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(result['success'], "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)))

    def test_all_problems_julia_success(self):
        for relative_filepath in glob.glob(os.path.join(self.julia_solutions_dir, "*.jl")):
            absolute_filepath = os.path.join(self.julia_solutions_dir, os.path.basename(relative_filepath))

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(result['success'], "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)))

    def test_all_problems_c_success(self):
        for relative_filepath in glob.glob(os.path.join(self.c_solutions_dir, "*.c")):
            absolute_filepath = os.path.join(self.c_solutions_dir, os.path.basename(relative_filepath))

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(result['success'], "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)))
