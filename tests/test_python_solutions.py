import json
import pytest

from helpers import get_solution_filepaths, problem_name_id


solution_files = get_solution_filepaths(language="python")


@pytest.mark.python
def test_python_solutions_exist():
    assert solution_files


@pytest.mark.python
@pytest.mark.parametrize("solution_file", solution_files, ids=problem_name_id)
def test_submit_file(solution_file, submit_solution):
    result = submit_solution(solution_file)

    assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
        json.dumps(result, indent=4)
    )
