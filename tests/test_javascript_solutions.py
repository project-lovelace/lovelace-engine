import glob
import json
import os

import pytest

from helpers import solutions_dir


# NOTE: If we make solution_files a fixture instead of a normal attr/function,
# then we can't use it in pytest's parametrize
solution_files = glob.glob(os.path.join(solutions_dir("javascript"), "*.js"))


@pytest.mark.javascript
def test_javascript_solutions_exist():
    assert solution_files


def id_func(param):
    problem_name, ext = os.path.splitext(os.path.basename(param))
    return problem_name


@pytest.mark.javascript
@pytest.mark.parametrize("solution_file", solution_files, ids=id_func)
def test_submit_file(solution_file, submit_solution):
    result = submit_solution(solution_file)

    assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
        json.dumps(result, indent=4)
    )
