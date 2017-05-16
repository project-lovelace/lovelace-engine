import base64
import falcon
import json
import logging

from problems.problem1 import Problem1
from runners.python_runner import PythonRunner
import util

# Config applies to all other loggers
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)


class SubmitResource(object):

    def on_post(self, req, resp):
        """Handle POST requests."""
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result_json = json.loads(raw_json.decode('utf-8'))
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body.')

        # Write user's code to file.
        code = result_json.get('code')
        if code:
            decoded_code = str(base64.b64decode(code), 'utf-8')
            code_filename = util.write_str_to_file(decoded_code)
            log.debug("User code saved in: %s", code_filename)
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'No code provided.')

        # Create a Problem1 instance which will come generated with several test cases.
        # TODO: Find a way of creating an instance of a specific depending on some variable passed by the user.
        # Then this file will apply to every problem.
        problem = Problem1()

        n = 1  # test case counter
        num_cases = len(problem.test_cases)
        successes = [None]*num_cases
        details_html = '<p>'

        for tc in problem.test_cases:
            input_str = tc.input_str()
            log.info("Test case %d/%d [type:%s].", n, num_cases, tc.test_type.name)
            details_html += 'Test case {:d}/{:d} [type:{}]: '.format(n, num_cases, tc.test_type.name)

            log.debug("Input string:")
            log.debug("%s", input_str)

            user_answer = PythonRunner().run(code_filename, input_str)

            log.debug("Output string:")
            log.debug("%s", user_answer)

            success = problem.verify_user_solution(input_str, user_answer)

            if success:
                successes[n-1] = True
                log.info("Test case passed!")
                details_html += 'passed!<br>'
            else:
                successes[n-1] = False
                log.info("Test case failed.")
                details_html += 'failed.<br>'

            # TODO: Pretty up this HTML.
            details_html += 'Input:<br>' + '<div style="font-family: monospace;">' + input_str + '</div><br>'
            details_html += 'Your output:<br>' + '<div style="font-family: monospace;">' + user_answer + '</div><br>'

            n = n+1

        passes = 0
        for success in successes:
            if success:
                passes += 1

        log.info("Passed %d/%d test cases.", passes, num_cases)
        details_html += 'Passed {:d}/{:d} test cases.<br>'.format(passes, num_cases)
        details_html += '</p>'

        all_solved = True if passes == num_cases else False

        resp_dict = {
            'details': details_html,
            'success': True if all_solved else False
        }

        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(resp_dict)

        util.delete_file(code_filename)
        log.debug("User code file deleted: %s", code_filename)


app = falcon.API()
app.add_route('/submit', SubmitResource())
