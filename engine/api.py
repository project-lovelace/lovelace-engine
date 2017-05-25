import base64
import falcon
import json
import logging

from engine.runners.python_runner import PythonRunner
import engine.util as util

# Config applies to all other loggers
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            logger.debug("User code saved in: %s", code_filename)
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'No code provided.')

        # Create a Problem1 instance which will come generated with several test cases.
        # TODO: Find a better way of deciding which problem to create an instance of.
        problem_id = int(result_json.get('problemID'))
        if problem_id == 1:
            import problems.problem1 as problem
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON.', 'Invalid problem ID.')

        # Generate a bunch of test cases.from 
        test_cases = problem.generate_test_cases()
        n_cases = len(test_cases)

        n = 1  # test case counter
        passes = [None]*n_cases
        details_html = '<p>'
        test_case_details = ''

        for tc in test_cases:
            input_str = tc.input_str()
            logger.info("Test case %d/%d (%s).", n, n_cases, tc.test_type.test_name)
            tc_panel_title = 'Test case {:d}/{:d} ({}): '.format(n, n_cases, tc.test_type.test_name)

            logger.debug("Input string:")
            logger.debug("%s", input_str)

            user_answer, process_info = PythonRunner().run(code_filename, input_str)

            logger.debug("Output string:")
            logger.debug("%s", user_answer)

            p_info_str = 'Return code {:d}, utime: {:f} s, stime: {:f} s, maxrss: {:d} kB.<br>'\
                .format(process_info['return_code'], process_info['utime'], process_info['stime'],
                        process_info['maxrss'])  # resource
            #           process_info['rss'])  # psutil

            passed = problem.verify_user_solution(input_str, user_answer)

            if passed:
                passes[n-1] = True
                logger.info("Test case passed!")
                tc_panel_title += 'passed!'
            else:
                passes[n-1] = False
                logger.info("Test case failed.")
                tc_panel_title += 'failed.'

            test_case_details += '<div class="panel panel-default">'\
                                 + '<div class="panel-heading" style="font-size: medium;">' + tc_panel_title + '</div>'\
                                 + '<div class="panel-body" style="font-family: monospace; font-size: medium;">'\
                                 + p_info_str\
                                 + 'Input:<br>' + input_str + '<br><br>'\
                                 + 'Output:<br>' + user_answer + '</div>'\
                                 + '</div>'
            n = n+1

        n_passes = sum(passes)  # Turns out you can sum booleans (True=1, False=0).

        logger.info("Passed %d/%d test cases.", n_passes, n_cases)
        details_html += 'Passed {:d}/{:d} test cases.<br>'.format(n_passes, n_cases)
        details_html += test_case_details + '</p>'

        all_solved = True if n_passes == n_cases else False

        resp_dict = {
            'details': details_html,
            'success': True if all_solved else False
        }

        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(resp_dict)

        util.delete_file(code_filename)
        logger.debug("User code file deleted: %s", code_filename)


app = falcon.API()
app.add_route('/submit', SubmitResource())
