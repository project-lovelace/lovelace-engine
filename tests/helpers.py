import os

# User can set solutions dir and server/port for lovelace engine if it's different from
# the default. Don't forget http:// at the beginning of the engine URI
# export LOVELACE_ENGINE_URI="https://custom-url:12345"
# export LOVELACE_SOLUTIONS_DIR="/home/myuser/lovelace/solutions"


def solutions_dir(language=""):
    sol_dir = os.environ.get("LOVELACE_SOLUTIONS_DIR", "/home/ada/lovelace/lovelace-solutions/")
    if language:
        sol_dir = os.path.join(sol_dir, language)
    if not os.path.isdir(sol_dir):
        raise ValueError(
            "Cannot find solutions dir at: {}. "
            "Is the env var LOVELACE_SOLUTIONS_DIR set properly?".format(sol_dir)
        )
    return sol_dir
