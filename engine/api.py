import base64
import falcon
import json
import logging
import importlib

from engine.runners.python_runner import PythonRunner
import engine.util as util

# Config applies to all other loggers
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)
# logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s', level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class SubmitResource(object):
    def on_post(self, req, resp):
        """Handle POST requests."""
        payload = parse_payload(req)
        code_filename = write_code_to_file(payload['code'], payload['language'])

        # Fetch problem ID and load the correct problem module.
        problem_name = payload['problem'].replace('-', '_')
        problem_module = 'problems.{}'.format(problem_name)
        try:
            problem = importlib.import_module(problem_module)
        except Exception:
            logger.error("Could not import module %s", problem_module)
            logger.error("Returning HTTP 400 Bad Request due to possibly invalid JSON.")
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'Invalid problem name!')
        else:
            test_case_type_enum = problem.TEST_CASE_TYPE_ENUM

        logger.info("Generating test cases...")
        test_cases = []
        for i, test_type in enumerate(test_case_type_enum):
            for _ in range(test_type.multiplicity):
                logger.debug("Generating test case {}...".format(i+1))
                test_cases.append(problem.generate_input(test_type))

        num_passes = 0
        num_cases = len(test_cases)
        test_case_details = []  # List of dicts each containing the details of a particular test case.

        for i, tc in enumerate(test_cases):
            input_str = tc.input_str()
            user_answer, process_info = PythonRunner().run(code_filename, input_str)
            passed = problem.verify_user_solution(input_str, user_answer)

            logger.info("Test case %d/%d (%s).", i+1, num_cases, tc.test_type.test_name)
            logger.debug("Input string:")
            logger.debug("%s", input_str)
            logger.debug("Output string:")
            logger.debug("%s", user_answer)

            if passed:
                num_passes += 1
                logger.info("Test case passed!")
            else:
                logger.info("Test case failed.")

            test_case_details.append({
                'testCaseType': tc.test_type.test_name,
                'inputString': input_str,
                'outputString': user_answer,
                'inputDict': tc.input,
                'outputDict': tc.output,  # TODO: This is our solution. We should be using the user's soluton.
                'passed': passed,
                'processInfo': process_info
            })

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
        logger.debug("User code file deleted: %s", code_filename)


def parse_payload(http_request):
    try:
        raw_payload_data = http_request.stream.read().decode('utf-8')
    except Exception as ex:
        logger.error('Bad request, reason unknown. Returning 400')
        raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

    try:
        json_payload = json.loads(raw_payload_data)
    except ValueError:
        logger.error('Received invalid JSON: {}'.format(raw_payload_data))
        logger.error('Returning 400 error')
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
    extension = {'python3': '.py'}.get(language)
    code_filename = util.write_str_to_file(decoded_code, extension)
    logger.debug('User code saved in: {}'.format(code_filename))

    return code_filename


app = falcon.API()
app.add_route('/submit', SubmitResource())
