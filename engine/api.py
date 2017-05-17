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
        # TODO: Find a better way of deciding which problem to create an instance of.
        problem_id = int(result_json.get('problemID'))
        if problem_id == 1:
            problem = Problem1()
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'Invalid problem ID.')

        n = 1  # test case counter
        num_cases = len(problem.test_cases)
        successes = [None]*num_cases
        details_html = '<p>'
        test_case_details = ''

        for tc in problem.test_cases:
            input_str = tc.input_str()
            log.info("Test case %d/%d (%s).", n, num_cases, tc.test_type.test_name)
            tc_panel_title = 'Test case {:d}/{:d} ({}): '.format(n, num_cases, tc.test_type.test_name)

            log.debug("Input string:")
            log.debug("%s", input_str)

            user_answer = PythonRunner().run(code_filename, input_str)

            log.debug("Output string:")
            log.debug("%s", user_answer)

            success = problem.verify_user_solution(input_str, user_answer)

            if success:
                successes[n-1] = True
                log.info("Test case passed!")
                tc_panel_title += 'passed!'
            else:
                successes[n-1] = False
                log.info("Test case failed.")
                tc_panel_title += 'failed.'

            test_case_details += '<div class="panel panel-default">'\
                                 + '<div class="panel-heading" style="font-size: medium;">' + tc_panel_title + '</div>'\
                                 + '<div class="panel-body" style="font-family: monospace; font-size: medium;">'\
                                 + 'Input:<br>' + input_str + '<br><br>'\
                                 + 'Output:<br>' + user_answer + '</div>'\
                                 + '</div>'
            n = n+1

        passes = 0
        for success in successes:
            if success:
                passes += 1

        log.info("Passed %d/%d test cases.", passes, num_cases)
        details_html += 'Passed {:d}/{:d} test cases.<br>'.format(passes, num_cases)
        details_html += test_case_details + '</p>'

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
