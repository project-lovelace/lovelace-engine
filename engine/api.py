import base64
import importlib
import json
import logging
import os
import shutil
import datetime

# Config applies to loggers created in modules accessed from this module
# Logger must loaded before importing other modules that rely on this logger,
# otherwise they will be getting an empty logger and messages from that module
# will not be logged.
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)

import falcon

import engine.util as util
from engine.simple_lxd import simple_lxd as lxd
from engine.runners.python_runner import PythonRunner, FilePushError, FilePullError, EngineExecutionError

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

    # This doesn't actually stop and delete the LXD containers if SIGKILL or SIGTERM was sent
    # as I think Python shuts down too quickly. TODO: Figure out how to unconditionally stop
    # and delete orphaned LXD containers.
    def __del__(self):
        lxd.stop(self.container_name, log=False)
        lxd.delete(self.container_name, log=False)

    def on_post(self, req, resp):
        """Handle POST requests."""
        # payload = parse_payload(req)
        payload = req.media

        code_filename = write_code_to_file(payload['code'], payload['language'])

        # Fetch problem ID and load the correct problem module.
        problem_name = payload['problem'].replace('-', '_')
        problem_module = 'problems.{:s}'.format(problem_name)
        logger.debug("problem_name={:s} problem_module={:s}".format(problem_name, problem_module))

        try:
            problem = importlib.import_module(problem_module)
        except Exception:
            logger.exception("Could not import module {:s}".format(problem_module))
            logger.error("Returning HTTP 400 Bad Request due to possibly invalid JSON.")
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'Invalid problem name!')
        else:
            test_case_type_enum = problem.TEST_CASE_TYPE_ENUM
            function_name = problem.FUNCTION_NAME
            problem_dir = problem_name
            static_resources = []

            for resource_file_name in problem.STATIC_RESOURCES:
                from_path = os.path.join(cwd, '..', 'resources', problem_dir, resource_file_name)
                to_path = os.path.join(cwd, resource_file_name)

                logger.debug("Copying static resource from {:s} to {:s}".format(from_path, to_path))

                try:
                    shutil.copyfile(from_path, to_path)
                except Exception:
                    resp.status = falcon.HTTP_500
                    resp.set_header('Access-Control-Allow-Origin', '*')
                    resp.body = json.dumps({'error': '500 Internal server error: Engine failed to find a resource.'})
                    return

                static_resources.append(to_path)

                container_path = "/root/{:}".format(resource_file_name)
                logger.debug("Pushing static resource to container {:}{:}".format(self.container_name, container_path))
                lxd.file_push(self.container_name, from_path, container_path)

        logger.info("Generating test cases...")
        test_cases = []
        for i, test_type in enumerate(test_case_type_enum):
            for j in range(test_type.multiplicity):
                logger.debug("Generating test case {:d}: {:s} ({:d}/{:d})..."
                    .format(len(test_cases)+1, str(test_type), j+1, test_type.multiplicity))
                test_cases.append(problem.generate_test_case(test_type))

        num_passes = 0  # Number of test cases passed.
        num_cases = len(test_cases)
        test_case_details = []  # List of dicts each containing the details of a particular test case.

        for i, tc in enumerate(test_cases):
            if 'DYNAMIC_RESOURCES' in tc.input:
                dynamic_resources = []
                for dynamic_resource_filename in tc.input['DYNAMIC_RESOURCES']:
                    resource_path = os.path.join(cwd, '..', 'resources', problem_dir, dynamic_resource_filename)
                    destination_path = os.path.join(cwd, dynamic_resource_filename)

                    logger.debug("Copying test case resource from {:s} to {:s}"
                        .format(resource_path, destination_path))

                    shutil.copyfile(resource_path, destination_path)
                    dynamic_resources.append(destination_path)

                    container_path = "/root/{:}".format(dynamic_resource_filename)
                    logger.debug("Pushing static resource to container {:}{:}".format(self.container_name, container_path))
                    lxd.file_push(self.container_name, resource_path, container_path)

            input_tuple = tc.input_tuple()
            logger.debug("Input tuple: {:}".format(input_tuple))

            if language == 'python3':
                runner = PythonRunner()
            elif language == 'javascript':
                runner = JavascriptRunner()
            else:
                raise Exception('Runner not found.')

            try:
                user_answer, process_info = runner.run(self.container_name, code_filename, function_name, input_tuple)
            except (FilePushError, FilePullError) as e:
                logger.error("File could not be pushed to or pulled from LXD container. Returning falcon HTTP 500.")

                resp_dict = {'error': "{:}".format(e)}
                resp.status = falcon.HTTP_500
                resp.set_header('Access-Control-Allow-Origin', '*')
                resp.body = json.dumps(resp_dict)
                return
            except EngineExecutionError as e:
                logger.warning("Return code from executing user code in LXD container is nonzero. Returning falcon HTTP 400.")

                resp_dict = {'error': "{:}".format(e)}
                resp.status = falcon.HTTP_400
                resp.set_header('Access-Control-Allow-Origin', '*')
                resp.body = json.dumps(resp_dict)
                return


            logger.debug("User answer: {:}".format(user_answer))
            logger.debug("Process info: {:}".format(process_info))

            if 'USER_GENERATED_FILES' in tc.input:
                for user_generated_filename in tc.input['USER_GENERATED_FILES']:
                    container_filepath = "/root/{:}".format(user_generated_filename)
                    logger.debug("Pulling user generated file from container {:}{:}"
                            .format(self.container_name, container_filepath))
                    lxd.file_pull(self.container_name, container_filepath, user_generated_filename)

            if user_answer[0] is None:
                logger.debug("Looks like user's function returned None; the output: {}".format(user_answer))
                passed = False
            else:
                passed = problem.verify_user_solution(input_tuple, user_answer)

            logger.info("Test case %d/%d (%s).", i+1, num_cases, tc.test_type.test_name)
            logger.debug("Input tuple:")
            logger.debug("%s", input_tuple)
            logger.debug("User answer:")
            logger.debug("%s", user_answer)

            if passed:
                num_passes += 1
                logger.info("Test case passed!")
            else:
                logger.info("Test case failed.")

            test_case_details.append({
                'testCaseType': tc.test_type.test_name,
                'inputString': str(input_tuple),
                'outputString': str(user_answer),
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
    if not code:
        raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'No code provided in request.')

    decoded_code = str(base64.b64decode(code), 'utf-8')
    extension = {'python3': '.py', 'julia': '.jl', 'javascript': '.js'}.get(language)
    code_filename = util.write_str_to_file(decoded_code, extension)

    logger.debug("User code saved in: {:s}".format(code_filename))

    return code_filename

app = falcon.API()
app.add_route('/submit', SubmitResource())
app.add_error_handler(
    Exception,
    lambda ex, req, resp, params: logger.exception(ex)
)
util.configure_lxd()
