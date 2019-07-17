import os
import json
import base64
import shutil
import urllib
import logging
import datetime
import importlib
import traceback

import falcon

import engine.util as util
from engine.simple_lxd import simple_lxd as lxd
from engine.runners.python_runner import PythonRunner, FilePushError, FilePullError, EngineExecutionError
from engine.runners.javascript_runner import JavascriptRunner
from engine.runners.julia_runner import JuliaRunner

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.ini")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

cwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(cwd)


class SubmitResource(object):
    def __init__(self):
        self.pid = os.getpid()
        self.container_image = "lovelace-image"
        self.container_name = "lovelace-{:d}-{:s}".format(self.pid, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

        logger.info("Launching Linux container {:s} (pid={:d}) from image {:s}..."
                    .format(self.container_name, self.pid, self.container_image))

        lxd.launch(self.container_image, name=self.container_name, profile="lovelace")

    def on_post(self, req, resp):
        payload = req.media

        code = payload['code']
        language = payload['language']

        if not code:
            resp_dict = {'error': "No code provided!"}
            resp.status = falcon.HTTP_400
            resp.set_header('Access-Control-Allow-Origin', '*')
            resp.body = json.dumps(resp_dict)
            return

        code_filename = write_code_to_file(code, language)

        try:
            # Fetch problem ID and load the correct problem module.
            problem_name = payload['problem'].replace('-', '_')
            problem_module = 'problems.{:s}'.format(problem_name)

            logger.debug("Importing problem_name={:s} problem_module={:s}...".format(problem_name, problem_module))

            problem = importlib.import_module(problem_module)
        except Exception:
            explanation = "Could not import module {:s}. " \
                          "Returning HTTP 400 Bad Request due to possibly invalid JSON.".format(problem_module)
            add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_400, code_filename)
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
                add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename)
                return

            static_resources.append(to_path)

            container_path = "/root/{:}".format(resource_file_name)
            logger.debug("Pushing static resource to container {:}{:}".format(self.container_name, container_path))
            lxd.file_push(self.container_name, from_path, container_path)

        logger.info("Generating test cases...")
        test_cases = []

        try:
            for i, test_type in enumerate(problem.TestCaseType):
                for j in range(test_type.multiplicity):
                    logger.debug("Generating test case {:d}: {:s} ({:d}/{:d})..."
                                 .format(len(test_cases)+1, str(test_type), j+1, test_type.multiplicity))
                    test_cases.append(problem.generate_test_case(test_type))
        except Exception:
            explanation = "Engine failed to generate a test case. Returning falcon HTTP 500."
            add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename)
            return

        num_passes = 0  # Number of test cases passed.
        num_cases = len(test_cases)
        test_case_details = []  # List of dicts each containing the details of a particular test case.

        for i, tc in enumerate(test_cases):
            if 'DYNAMIC_RESOURCES' in tc.input:
                dynamic_resources = []
                for dynamic_resource_filename in tc.input['DYNAMIC_RESOURCES']:
                    resource_path = os.path.join(cwd, "..", "resources", problem_dir, dynamic_resource_filename)
                    destination_path = os.path.join(cwd, dynamic_resource_filename)

                    logger.debug("Copying test case resource from {:s} to {:s}".format(resource_path, destination_path))

                    shutil.copyfile(resource_path, destination_path)
                    dynamic_resources.append(destination_path)

                    container_path = "/root/{:}".format(dynamic_resource_filename)
                    logger.debug("Pushing static resource to container {:}{:}".format(self.container_name, container_path))
                    lxd.file_push(self.container_name, resource_path, container_path)

            input_tuple = tc.input_tuple()
            logger.debug("Input tuple: {:}".format(input_tuple))

            if language == 'python':
                runner = PythonRunner()
            elif language == 'javascript':
                runner = JavascriptRunner()
            elif language == 'julia':
                runner = JuliaRunner()
            else:
                raise Exception('Runner not found.')

            try:
                user_answer, process_info = runner.run(self.container_name, code_filename, function_name, input_tuple)

            except (FilePushError, FilePullError):
                explanation = "File could not be pushed to or pulled from LXD container. Returning falcon HTTP 500."
                add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename)
                return

            except EngineExecutionError:
                explanation = "Return code from executing user code in LXD container is nonzero. " \
                              "Returning falcon HTTP 400."
                add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_400, code_filename)
                return

            if 'USER_GENERATED_FILES' in tc.input:
                for user_generated_filename in tc.input['USER_GENERATED_FILES']:
                    container_filepath = "/root/{:}".format(user_generated_filename)

                    logger.debug("Pulling user generated file from container {:}{:}"
                                 .format(self.container_name, container_filepath))

                    lxd.file_pull(self.container_name, container_filepath, user_generated_filename)

            if user_answer[0] is None:
                logger.debug("Looks like user's function returned None: output={:}".format(user_answer))
                passed = False
            else:
                try:
                    passed, expected = problem.verify_user_solution(input_tuple, user_answer)
                except Exception:
                    explanation = "Internal engine error during user test case verification. Returning falcon HTTP 500."
                    add_error_to_response(resp, explanation, traceback.format_exc(), falcon.HTTP_500, code_filename)
                    return

            if passed:
                num_passes += 1

            test_case_details.append({
                'testCaseType': tc.test_type.test_name,
                'inputString': str(input_tuple),
                'outputString': str(user_answer),
                'expectedString': str(expected),
                'passed': passed,
                'processInfo': process_info
            })

            if 'DYNAMIC_RESOURCES' in tc.input:
                for dynamic_resource_path in dynamic_resources:
                    logger.debug("Deleting dynamic resource: {:s}".format(dynamic_resource_path))
                    os.remove(dynamic_resource_path)

        logger.info("Passed %d/%d test cases.", num_passes, num_cases)

        resp_dict = {
            'success': True if num_passes == num_cases else False,
            'numTestCases': num_cases,
            'numTestCasesPassed': num_passes,
            'testCaseDetails': test_case_details
        }

        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(resp_dict)

        util.delete_file(code_filename)
        logger.debug("User code file deleted: {:s}".format(code_filename))

        for file_path in static_resources:
            logging.debug("Deleting static resource {:s}".format(file_path))
            os.remove(file_path)


def parse_payload(http_request):
    try:
        raw_payload_data = http_request.stream.read().decode('utf-8')
    except Exception as ex:
        logger.error("Bad request, reason unknown. Returning 400.")
        raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

    try:
        json_payload = json.loads(raw_payload_data)
    except ValueError:
        logger.error("Received invalid JSON: {:}".format(raw_payload_data))
        logger.error("Returning 400 error.")
        raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode request body.')

    return json_payload


def write_code_to_file(code, language):
    """
    Write code into a file with the appropriate file extension.

    :param code: a base64 encoded string representing the user's submitted source code
    :param language: the code's programming language
    :return: the name of the file containing the user's code
    """
    decoded_code = str(base64.b64decode(code), 'utf-8')
    extension = {'python': '.py', 'julia': '.jl', 'javascript': '.js'}.get(language)
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

    url_friendly_tb = urllib.parse.quote(tb)  # URL friendly traceback we can embed into a mailto: link.

    DISCOURSE_LINK = '<a href="https://discourse.projectlovelace.net/">https://discourse.projectlovelace.net/</a>'
    EMAIL_LINK = '<a href="mailto:ada@projectlovelace.net?&subject=Project Lovelace error report' \
                 + '&body={:}%0A%0A{:}'.format(explanation, url_friendly_tb) + '">ada@mg.projectlovelace.net</a>'

    NOTICE = "You should not be seeing this error :( If you have the time, we'd really appreciate\n" \
             "if you could report this on Discourse (" + DISCOURSE_LINK + ") or\n" \
             "via email (" + EMAIL_LINK + "). All the information is embedded in the email link\n" \
             "so all you have to do is press send. Thanks so much!"

    error_message = "{:s}\n\n{:s}\n\nError: {:}".format(explanation, NOTICE, tb)
    resp_dict = {'error': error_message}

    resp.status = falcon_http_error_code
    resp.set_header('Access-Control-Allow-Origin', '*')
    resp.body = json.dumps(resp_dict)
    return


app = falcon.API()
app.add_route('/submit', SubmitResource())
app.add_error_handler(
    Exception,
    lambda ex, req, resp, params: logger.exception(ex)
)
util.configure_lxd()
