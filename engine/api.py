import base64
import falcon
import json
import logging
import importlib

from engine.runners.python_runner import PythonRunner
import engine.util as util

# Config applies to all other loggers
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SubmitResource(object):
    def on_post(self, req, resp):
        """Handle POST requests."""
        payload = parse_payload(req)
        code_filename = write_code_to_file(payload.get('code'))

        # Fetch problem ID and load the correct problem module.
        problem_name = payload.get('problem')
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

        # Count number of test cases we'll be generating in total.
        n_cases = 0
        for test_type in test_case_type_enum:
            n_cases += test_type.multiplicity

        # Generate all the cases and store them in test_cases.
        n = 1
        for test_type in test_case_type_enum:
            for _ in range(test_type.multiplicity):
                logger.debug("Generating test case %d/%d...", n, n_cases)
                test_cases.append(problem.generate_input(test_type))
                n += 1

        n = 1  # test case counter
        n_passes = 0
        test_case_details = []  # List of dicts each containing the details of a particular test case.

        for tc in test_cases:
            input_str = tc.input_str()
            user_answer, process_info = PythonRunner().run(code_filename, input_str)
            passed = problem.verify_user_solution(input_str, user_answer)

            logger.info("Test case %d/%d (%s).", n, n_cases, tc.test_type.test_name)
            logger.debug("Input string:")
            logger.debug("%s", input_str)
            logger.debug("Output string:")
            logger.debug("%s", user_answer)

            if passed:
                n_passes += 1
                logger.info("Test case passed!")
            else:
                logger.info("Test case failed.")

            n = n+1
            test_case_details.append({
                'testCaseType': tc.test_type.test_name,
                'inputString': input_str,
                'outputString': user_answer,
                'inputDict': tc.input,
                'outputDict': tc.output,  # TODO: This is our solution. We should be using the user's soluton.
                'passed': passed,
                'processInfo': process_info
            })

        logger.info("Passed %d/%d test cases.", n_passes, n_cases)

        resp_dict = {
            'success': True if n_passes == n_cases else False,
            'numTestCases': n_cases,
            'numTestCasesPassed': n_passes,
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


def write_code_to_file(code):
    """
    :param code: a base64 encoded string representing the user's submitted file 
    :return: the name of the file containing the user's code
    """
    if code:
        decoded_code = str(base64.b64decode(code), 'utf-8')
        code_filename = util.write_str_to_file(decoded_code)
        logger.debug("User code saved in: %s", code_filename)
    else:
        raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'No code provided in request.')

    return code_filename


app = falcon.API()
app.add_route('/submit', SubmitResource())
