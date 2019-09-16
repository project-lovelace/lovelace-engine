import base64
import json
import os

import pytest
import requests


# User can set solutions dir and server/port for lovelace engine if it's different from
# the default. Don't forget http:// at the beginning of the engine URI
# export LOVELACE_ENGINE_URI="https://custom-url:12345"
# export LOVELACE_SOLUTIONS_DIR="/home/myuser/lovelace/solutions"


@pytest.fixture(scope="session")
def engine_uri():
    uri = os.environ.get("LOVELACE_ENGINE_URI", "http://localhost:14714")
    err_msg = (
        "Cannot connect to lovelace engine at {}. Is it running? "
        "Check if the env var LOVELACE_ENGINE_URI is set properly. ".format(uri)
    )
    try:
        resp = requests.get(uri)
    except requests.exceptions.ConnectionError:
        raise ValueError(err_msg)
    if resp.ok is not True:
        raise ValueError(err_msg)
    return uri


@pytest.fixture()
def engine_submit_uri(engine_uri):
    return engine_uri + "/submit"


@pytest.fixture(scope="session")
def solutions_dir():
    sol_dir = os.environ.get("LOVELACE_SOLUTIONS_DIR", "/home/ada/lovelace/lovelace-solutions/")
    if not os.path.isdir(sol_dir):
        raise ValueError(
            "Cannot find solutions dir at: {}. "
            "Is the env var LOVELACE_SOLUTIONS_DIR set properly?".format(sol_dir)
        )
    return sol_dir


@pytest.fixture()
def language_solutions_dir(solutions_dir):
    def language_solutions_dir_helper(language):
        return os.path.join(solutions_dir, language)

    return language_solutions_dir_helper


@pytest.fixture
def submit_solution():
    def submit_solution_helper(file_path, engine_submit_uri):
        with open(file_path, "r") as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode("utf-8")).decode("utf-8")

        problem_name, extension = os.path.basename(file_path).split(sep=".")
        language = {"py": "python", "js": "javascript", "jl": "julia", "c": "c"}.get(extension)

        payload_dict = {"problem": problem_name, "language": language, "code": code_b64}
        payload_json = json.dumps(payload_dict)

        response = requests.post(engine_submit_uri, data=payload_json)
        response_data = json.loads(response.text)

        return response_data

    return submit_solution_helper
