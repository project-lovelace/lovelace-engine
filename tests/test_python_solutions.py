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
