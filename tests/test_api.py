import os
import glob
import time
import json
import base64
import requests
import unittest


# User can set solutions dir and server/port for lovelace engine if it's different from
# the default. Don't forget http:// at the beginning of the engine URI
ENGINE_URI = os.environ.get("LOVELACE_ENGINE_URI", "http://localhost:14714")
SOLUTIONS_DIR = os.environ.get("LOVELACE_SOLUTIONS_DIR", "/home/ada/lovelace/lovelace-solutions/")
print("SOLUTIONS_DIR: ", SOLUTIONS_DIR)
print("ENGINE_URI: ", ENGINE_URI)


def test_environment_solutions_dir():
    assert os.path.isdir(SOLUTIONS_DIR) is True


def test_environment_engine_uri():
    resp = requests.get(ENGINE_URI)
    assert resp.ok is True


class TestApi(unittest.TestCase):

    python_solutions_dir = os.path.join(SOLUTIONS_DIR, "python")
    javascript_solutions_dir = os.path.join(SOLUTIONS_DIR, "javascript")
    julia_solutions_dir = os.path.join(SOLUTIONS_DIR, "julia")
    c_solutions_dir = os.path.join(SOLUTIONS_DIR, "c")

    @staticmethod
    def submit_solution(file_path):
        with open(file_path, "r") as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("utf-8")

        problem_name, extension = os.path.basename(file_path).split(sep=".")
        language = {"py": "python", "js": "javascript", "jl": "julia", "c": "c"}.get(extension)

        payload_dict = {"problem": problem_name, "language": language, "code": code_b64}
        payload_json = json.dumps(payload_dict)

        response = requests.post(ENGINE_URI + "/submit", data=payload_json)
        response_data = json.loads(response.text)

        return response_data

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
