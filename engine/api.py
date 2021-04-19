import atexit
import base64
import datetime
import importlib
import json
import logging
import os
import shutil
import subprocess
import traceback
import urllib

import falcon

import engine.util as util

from engine.code_runner import CodeRunner, FilePushError, FilePullError, EngineExecutionError
from engine.docker_util import (
    docker_init,
    docker_file_push,
    docker_file_pull,
    create_docker_container,
    remove_docker_container,
)


log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.ini")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)


class SubmitResource:
    def __init__(self):
        self.pid = os.getpid()
        # self.container_image = "lovelace-image"
        container_name = "lovelace-{:d}-{:s}".format(
            self.pid, datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        )

        # Start a container to use for all submissions
        # TODO this container_name might not be unique!
        self.container_id, self.container_name = create_docker_container(name=container_name)
        logger.debug(
            "Docker container id: {}; name: {}".format(self.container_id, self.container_name)
        )

        atexit.register(remove_docker_container, self.container_id)

    def on_post(self, req, resp):
        payload = req.media

        code = payload["code"]
        language = payload["language"]

        if not code:
            resp_dict = {"error": "No code provided!"}
            resp.status = falcon.HTTP_400
            resp.set_header("Access-Control-Allow-Origin", "*")
            resp.body = json.dumps(resp_dict)
            return

        code_filename = write_code_to_file(code, language)

        try:
            # Fetch problem ID and load the correct problem module.
            problem_name = payload["problem"].replace("-", "_")
            problem_module = "problems.{:s}".format(problem_name)

            logger.debug(
                "Importing problem_name={:s} problem_module={:s}...".format(
                    problem_name, problem_module
                )
            )

            problems = importlib.import_module("problems")
            problem = importlib.import_module(problem_module)
        except Exception:
            explanation = (
                "Could not import module {:s}. "
                "Returning HTTP 400 Bad Request due to possibly invalid JSON.".format(
                    problem_module
                )
            )
            add_error_to_response(
                resp, explanation, traceback.format_exc(), falcon.HTTP_400, code_filename
            )
            return

        function_name = problem.FUNCTION_NAME
        problem_dir = problem_name

        # Copy static resources into engine directory and push them into the Linux container.
        static_resources = []
        for resource_file_name in problem.STATIC_RESOURCES:
            from_path = os.path.join(cwd, "..", "resources", problem_dir, resource_file_name)
            to_path = os.path.join(cwd, resource_file_name)

            logger.debug("Copying static resource from {:s} to {:s}".format(from_path, to_path))

            try:
                shutil.copyfile(from_path, to_path)
            except Exception:
                explanation = "Engine failed to copy a static resource. Returning falcon HTTP 500."
                add_error_to_response(
                    resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename
                )
                return

            static_resources.append(to_path)

            container_path = "/root/{:}".format(resource_file_name)
            logger.debug(
                "Pushing static resource to container {:}{:}".format(
                    self.container_id, container_path
                )
            )
            _ = docker_file_push(self.container_id, from_path, container_path)

        if not problem.STATIC_RESOURCES:
            logger.debug("No static resources to push")

        logger.info("Generating test cases...")
        test_cases = []

        try:
            for i, test_type in enumerate(problem.TestCaseType):
                for j in range(test_type.multiplicity):
                    logger.debug(
                        "Generating test case {:d}: {:s} ({:d}/{:d})...".format(
                            len(test_cases) + 1, str(test_type), j + 1, test_type.multiplicity
                        )
                    )
                    test_cases.append(problem.generate_test_case(test_type))
        except Exception:
            explanation = "Engine failed to generate a test case. Returning falcon HTTP 500."
            add_error_to_response(
                resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename
            )
            return

        # Copy over all the dynamic resources generated by the test cases.
        dynamic_resources = []
        for i, tc in enumerate(test_cases):
            if "DYNAMIC_RESOURCES" in tc.input:
                for dynamic_resource_filename in tc.input["DYNAMIC_RESOURCES"]:
                    resource_path = os.path.join(
                        cwd, "..", "resources", problem_dir, dynamic_resource_filename
                    )
                    destination_path = os.path.join(cwd, dynamic_resource_filename)

                    logger.debug(
                        "Copying test case resource from {:s} to {:s}...".format(
                            resource_path, destination_path
                        )
                    )

                    shutil.copyfile(resource_path, destination_path)

                    dynamic_resources.append(resource_path)
                    dynamic_resources.append(destination_path)

                    container_path = "/root/{:}".format(dynamic_resource_filename)
                    logger.debug(
                        "Pushing dynamic resource to container {:}{:}".format(
                            self.container_id, container_path
                        )
                    )
                    _ = docker_file_push(self.container_id, resource_path, container_path)

        if not dynamic_resources:
            logger.debug("No dynamic resources to push")

        runner = CodeRunner(language)

        input_tuples = [tc.input_tuple() for tc in test_cases]
        output_tuples = [tc.output_tuple() for tc in test_cases]
        try:
            user_outputs, p_infos = runner.run(
                self.container_name, code_filename, function_name, input_tuples, output_tuples
            )
        except (FilePushError, FilePullError):
            explanation = "File could not be pushed to or pulled from docker container. Returning falcon HTTP 500."
            add_error_to_response(
                resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename
            )
            return

        except EngineExecutionError:
            explanation = (
                "Return code from executing user code in docker container is nonzero. "
                "Returning falcon HTTP 400."
            )
            add_error_to_response(
                resp, explanation, traceback.format_exc(), falcon.HTTP_400, code_filename
            )
            return

        # Pull any user generated files.
        files_pulled = False
        for i, tc in enumerate(test_cases):
            if "USER_GENERATED_FILES" in tc.output:
                for user_generated_filename in tc.output["USER_GENERATED_FILES"]:
                    container_filepath = "/root/{:s}".format(user_generated_filename)

                    logger.debug(
                        "Pulling user generated file from container {:s}{:s}".format(
                            self.container_name, container_filepath
                        )
                    )

                    _ = docker_file_pull(
                        self.container_id, container_filepath, user_generated_filename
                    )
                    files_pulled = True

        if not files_pulled:
            logger.debug("No user generated files to pull")

        n_cases = len(test_cases)
        n_passes = 0  # Number of test cases passed.
        test_case_details = (
            []
        )  # List of dicts each containing the details of a particular test case.

        # Verify that user outputs are all correct (i.e. check whether each test case passes or fails).
        for input_tuple, user_output, p_info, tc in zip(
            input_tuples, user_outputs, p_infos, test_cases
        ):

            if isinstance(user_output, list):
                # user_output is a list. This could be a multiple-return, or a legitimate list return.
                # Here we will disambiguate dependant on the output variables the problem requires
                if len(problem.OUTPUT_VARS) == 1:
                    # Only one variable should be returned; Thus, this is a "list return"
                    user_output = (user_output,)
                else:
                    # More than one variable should be returned, so this is a multiple return
                    user_output = tuple(user_output)

            if user_output[0] is None:
                logger.debug(
                    "Looks like user's function returned None: output={:}".format(user_output)
                )
                passed = False
                expected_output = "Your function returned None. It shouldn't do that."
            else:
                try:
                    user_test_case = problem.ProblemTestCase(None, problem.INPUT_VARS, input_tuple, problem.OUTPUT_VARS, user_output)
                    passed, correct_test_case = problems.test_case.test_case_solution_correct(tc, user_test_case, problem.ATOL, problem.RTOL)
                    expected_output = correct_test_case.output_tuple()
                except Exception:
                    explanation = "Internal engine error during user test case verification. Returning falcon HTTP 500."
                    add_error_to_response(
                        resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename
                    )
                    return

            if passed:
                n_passes += 1

            test_case_details.append(
                {
                    "testCaseType": tc.test_type.test_name,
                    "input": input_tuple,
                    "output": user_output,
                    "expected": expected_output,
                    "inputString": str(input_tuple),
                    "outputString": str(user_output),
                    "expectedString": str(expected_output),
                    "passed": passed,
                    "processInfo": p_info,
                }
            )

            if "DYNAMIC_RESOURCES" in tc.input:
                for dynamic_resource_path in dynamic_resources:
                    logger.debug("Deleting dynamic resource: {:s}".format(dynamic_resource_path))
                    util.delete_file(dynamic_resource_path)

        logger.info("Passed %d/%d test cases.", n_passes, n_cases)

        resp_dict = {
            "success": True if n_passes == n_cases else False,
            "numTestCases": n_cases,
            "numTestCasesPassed": n_passes,
            "testCaseDetails": test_case_details,
        }

        resp.status = falcon.HTTP_200
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.body = json.dumps(resp_dict)

        util.delete_file(code_filename)
        logger.debug("User code file deleted: {:s}".format(code_filename))

        for file_path in static_resources:
            logging.debug("Deleting static resource {:s}".format(file_path))
            util.delete_file(file_path)


def parse_payload(http_request):
    try:
        raw_payload_data = http_request.stream.read().decode("utf-8")
    except Exception as ex:
        logger.error("Bad request, reason unknown. Returning 400.")
        raise falcon.HTTPError(falcon.HTTP_400, "Error", ex.message)

    try:
        json_payload = json.loads(raw_payload_data)
    except ValueError:
        logger.error("Received invalid JSON: {:}".format(raw_payload_data))
        logger.error("Returning 400 error.")
        raise falcon.HTTPError(falcon.HTTP_400, "Invalid JSON", "Could not decode request body.")

    return json_payload


def write_code_to_file(code, language):
    """
    Write code into a file with the appropriate file extension.

    :param code: a base64 encoded string representing the user's submitted source code
    :param language: the code's programming language
    :return: the name of the file containing the user's code
    """
    decoded_code = str(base64.b64decode(code), "utf-8")
    extension = {"python": ".py", "javascript": ".js", "julia": ".jl", "c": ".c"}.get(language)
    code_filename = util.write_str_to_file(decoded_code, extension)

    logger.debug("User code saved in: {:s}".format(code_filename))

    return code_filename


def add_error_to_response(resp, explanation, tb, falcon_http_error_code, code_filename):
    """
    Modify the falcon HTTP response object with an error to be shown to the user. Also deletes the user's code as the
    engine cannot run it.

    :param resp: The falcon HTTP response object to be modified.
    :param explanation: A human-friendly explanation of the error.
    :param tb: Traceback string.
    :param falcon_http_error_code: Falcon HTTP error code to return.
    :param code_filename: Filepath to user code to be deleted.
    :return: nothing
    """
    logger.error(explanation)
    logger.error(tb)
    util.delete_file(code_filename)
    # URL friendly traceback we can embed into a mailto: link.
    url_friendly_tb = urllib.parse.quote(tb)

    DISCOURSE_LINK = '<a href="https://discourse.projectlovelace.net/">https://discourse.projectlovelace.net/</a>'
    EMAIL_LINK = (
        '<a href="mailto:ada@mg.projectlovelace.net?&subject=Project Lovelace error report'
        + "&body={:}%0A%0A{:}".format(explanation, url_friendly_tb)
        + '">ada@mg.projectlovelace.net</a>'
    )

    NOTICE = (
        "A stacktrace should appear below with more information about this error which might help\n"
        "you debug your code. But if it's not your code then it might be our fault :( If this is a\n"
        "website error and you have the time, we'd really appreciate it if you could report this\n"
        "on Discourse (" + DISCOURSE_LINK + ") or via email (" + EMAIL_LINK + ").\n"
        "All the information is embedded in the email link so all you have to do is press send.\n"
        "Thanks so much!"
    )

    error_message = "{:s}\n\n{:s}\n\nError: {:}".format(explanation, NOTICE, tb)
    resp_dict = {"error": error_message}

    resp.status = falcon_http_error_code
    resp.set_header("Access-Control-Allow-Origin", "*")
    resp.body = json.dumps(resp_dict)
    return


docker_init()
app = falcon.API()
app.add_route("/submit", SubmitResource())
app.add_error_handler(Exception, lambda ex, req, resp, params: logger.exception(ex))
