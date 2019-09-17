import glob
import json
import os
import time


import pytest

from helpers import solutions_dir


# NOTE: If we make solution files a fixture instead of a normal attr/function,
# then we can't use it in pytest's parametrize
solution_files = glob.glob(os.path.join(solutions_dir("python"), "*.py"))


@pytest.mark.python
def test_solutions_exist():
    assert solution_files


# TODO ids. id function to turn file name into cleaner label
@pytest.mark.python
@pytest.mark.parametrize("solution_file", solution_files)
def test_submit_file(solution_file, engine_submit_uri, submit_solution):
    result = submit_solution(solution_file, engine_submit_uri)

    assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
        json.dumps(result, indent=4)
    )


# @pytest.fixture
# def get_solution_files(solutions_dir):
#     def _get_solution_files():
#         return glob.glob(os.path.join(solutions_dir, "python", "*.py"))

#     return _get_solution_files


# @pytest.fixture(scope="class")
# def solution_files(request, solutions_dir):
#     files = glob.glob(os.path.join(solutions_dir, "python", "*.py"))
#     if request.cls is not None:
#         request.cls.solution_files = solution_files
#     return files


# TODO: how to use a fixture here?
# files_to_submit = ["almost_pi.py", "colorful_resistors.py"]
# files_to_submit = get_solution_files()


# # TODO: can't we get that engine_uri into the submit solution fixture?
# @pytest.mark.parametrize("solution_file", files_to_submit)
# def test_submit_file(solution_file, engine_submit_uri, submit_solution):
#     result = submit_solution(solution_file, engine_submit_uri)

#     assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
#         json.dumps(result, indent=4)
#     )


# class TestPythonSolutions:
#     # TODO: can't we get that engine_uri into the submit solution fixture?
#     @pytest.mark.parametrize("solution_file", self.solution_files)
#     def test_submit_file(self, solution_file, engine_submit_uri, submit_solution):
#         result = submit_solution(solution_file, engine_submit_uri)

#         assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
#             json.dumps(result, indent=4)
#         )


# def test_all_problems_python_success(language_solutions_dir, engine_submit_uri, submit_solution):
#     python_solutions_dir = language_solutions_dir("python")
#     solution_files = glob.glob(os.path.join(python_solutions_dir, "*.py"))
#     if not solution_files:
#         raise Exception("Couldn't find any python solution files to test")

#     for relative_filepath in solution_files:
#         absolute_filepath = os.path.join(python_solutions_dir, os.path.basename(relative_filepath))

#         print("Submitting {:}... ".format(absolute_filepath), end="", flush=True)
#         t1 = time.perf_counter()
#         result = submit_solution(absolute_filepath, engine_submit_uri)
#         t2 = time.perf_counter()
#         print("{:.6f} seconds.".format(t2 - t1))

#         assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
#             json.dumps(result, indent=4)
#         )
