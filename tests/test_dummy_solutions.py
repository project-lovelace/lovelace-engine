import os
import glob
import json
import pytest

from helpers import filename_id, ext2language


cwd = os.path.dirname(os.path.realpath(__file__))
solution_files = glob.glob(os.path.join(cwd, "dummy_solutions", "*"))


@pytest.mark.parametrize("solution_file", solution_files, ids=filename_id)
def test_dummy_solutions(solution_file, submit_solution):
    problem_name, ext = os.path.splitext(os.path.basename(solution_file))
    result = submit_solution(solution_file, problem_name, ext2language[ext[1:]])

    assert result.get("success") is True, "Failed. Engine output:\n{:}".format(
        json.dumps(result, indent=4)
    )
