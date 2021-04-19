import os
import glob

# User can set solutions and problems dir and server/port for lovelace engine if it's different
# from the default. Don't forget http:// at the beginning of the engine URI
# export LOVELACE_ENGINE_URI="https://custom-url:12345"
# export LOVELACE_SOLUTIONS_DIR="/home/myuser/lovelace/solutions"
# export LOVELACE_PROBLEMS_DIR="/home/myuser/lovelace/problems"

def solutions_dir(language=""):
    sol_dir = os.environ.get("LOVELACE_SOLUTIONS_DIR", "/home/ada/lovelace/lovelace-solutions/")
    if language:
        sol_dir = os.path.join(sol_dir, language)
    if not os.path.isdir(sol_dir):
        raise ValueError(
            f"Cannot find solutions dir at: {sol_dir}. "
            "Is the env var LOVELACE_SOLUTIONS_DIR set properly?"
        )
    return sol_dir

def problems_dir():
    prob_dir = os.environ.get("LOVELACE_PROBLEMS_DIR", "/home/ada/lovelace/lovelace-problems/")
    if not os.path.isdir(prob_dir):
        raise ValueError(
            f"Cannot find solutions dir at: {prob_dir}. "
            "Is the env var LOVELACE_PROBLEMS_DIR set properly?"
        )
    return prob_dir


language2ext = {"python": "py", "javascript": "js", "julia": "jl", "c": "c"}
ext2language = {"py": "python", "js": "javascript", "jl": "julia", "c": "c"}


def get_solution_filepaths(language=""):
    all_solution_filepaths = glob.glob(os.path.join(solutions_dir(language), f"*.{language2ext[language]}"))
    all_problem_filepaths = glob.glob(os.path.join(problems_dir(), "problems", "*.py"))

    solutions = [os.path.splitext(os.path.basename(fp))[0] for fp in all_solution_filepaths]
    problems = [os.path.splitext(os.path.basename(fp))[0] for fp in all_problem_filepaths]

    valid_solution_filepaths = []

    for (n, sol) in enumerate(solutions):
        # Might need to replace - with _ for Javascript solutions.
        if sol.replace("-", "_") in problems:
            valid_solution_filepaths.append(all_solution_filepaths[n])

    return valid_solution_filepaths


def problem_name_id(param):
    problem_name, ext = os.path.splitext(os.path.basename(param))
    return problem_name


def filename_id(param):
    return os.path.basename(param)
