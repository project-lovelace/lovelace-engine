import os
import glob
import time
import json
import base64
import requests
import unittest

import pytest


class TestApi(unittest.TestCase):
    @pytest.fixture(scope="class", autouse=True)
    def setup_solutions_dirs(self, solutions_dir):
        self.python_solutions_dir = os.path.join(solutions_dir, "python")
        self.javascript_solutions_dir = os.path.join(solutions_dir, "javascript")
        self.julia_solutions_dir = os.path.join(solutions_dir, "julia")
        self.c_solutions_dir = os.path.join(solutions_dir, "c")

    @pytest.fixture(scope="class", autouse=True)
    def setup_engine_uri(self, engine_uri):
        self.engine_uri = engine_uri

    def submit_solution(self, file_path):
        with open(file_path, "r") as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("utf-8")

        problem_name, extension = os.path.basename(file_path).split(sep=".")
        language = {"py": "python", "js": "javascript", "jl": "julia", "c": "c"}.get(extension)

        payload_dict = {"problem": problem_name, "language": language, "code": code_b64}
        payload_json = json.dumps(payload_dict)

        response = requests.post(self.engine_uri + "/submit", data=payload_json)
        response_data = json.loads(response.text)

        return response_data

    @pytest.mark.python
    def test_all_problems_python_success(self):
        solution_files = glob.glob(os.path.join(self.python_solutions_dir, "*.py"))
        if not solution_files:
            raise Exception("Couldn't find any python solution files to test")

        for relative_filepath in solution_files:
            absolute_filepath = os.path.join(
                self.python_solutions_dir, os.path.basename(relative_filepath)
            )

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(
                result["success"],
                "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)),
            )

    @pytest.mark.javascript
    def test_all_problems_javascript_success(self):
        solution_files = glob.glob(os.path.join(self.javascript_solutions_dir, "*.js"))
        if not solution_files:
            raise Exception("Couldn't find any javascript solution files to test")

        for relative_filepath in solution_files:
            absolute_filepath = os.path.join(
                self.javascript_solutions_dir, os.path.basename(relative_filepath)
            )

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(
                result["success"],
                "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)),
            )

    @pytest.mark.julia
    def test_all_problems_julia_success(self):

        solution_files = glob.glob(os.path.join(self.julia_solutions_dir, "*.jl"))
        if not solution_files:
            raise Exception("Couldn't find any julia solution files to test")

        for relative_filepath in solution_files:
            absolute_filepath = os.path.join(
                self.julia_solutions_dir, os.path.basename(relative_filepath)
            )

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(
                result["success"],
                "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)),
            )

    @pytest.mark.c
    def test_all_problems_c_success(self):

        solution_files = glob.glob(os.path.join(self.c_solutions_dir, "*.c"))
        if not solution_files:
            raise Exception("Couldn't find any c solution files to test")

        for relative_filepath in solution_files:
            absolute_filepath = os.path.join(
                self.c_solutions_dir, os.path.basename(relative_filepath)
            )

            print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
            t1 = time.perf_counter()
            result = self.submit_solution(absolute_filepath)
            t2 = time.perf_counter()
            print("{:.6f} seconds.".format(t2 - t1))

            self.assertTrue(
                result["success"],
                "Failed. Engine output:\n{:}".format(json.dumps(result, indent=4)),
            )
