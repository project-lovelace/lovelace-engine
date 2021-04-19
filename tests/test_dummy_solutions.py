import os
import glob
import json
import pytest

from helpers import filename_id, ext2language


cwd = os.path.dirname(os.path.realpath(__file__))
solution_files = glob.glob(os.path.join(cwd, "dummy_solutions", "*"))


# See: https://github.com/project-lovelace/lovelace-engine/issues/84
def test_84(submit_file):
    filepath = os.path.join(cwd, "dummy_solutions", "chaos_84.js")
    result = submit_file(filepath, problem="chaos", language="javascript")
    assert result.get("success") is True, f"Failed. Engine output:\n{json.dumps(result, indent=4)}"


def test_infinite_loop_times_out(submit_file):
    filepath = os.path.join(cwd, "dummy_solutions", "infinite_loop.py")
    with pytest.raises(Exception) as e_info:
        result = submit_file(filepath, problem="scientific_temperatures", language="python")


def test_memory_explosion_times_out(submit_file):
    filepath = os.path.join(cwd, "dummy_solutions", "memory_explosion.py")
    with pytest.raises(Exception) as e_info:
        result = submit_file(filepath, problem="speed_of_light", language="python")
