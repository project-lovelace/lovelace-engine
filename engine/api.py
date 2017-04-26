import base64
import falcon
import json
import logging

from problems.problem1 import Problem1
from engine.runners.python_runner import PythonRunner
import engine.util as util

logging.basicConfig()  # applies to all other loggers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class SubmitResource(object):

    def on_post(self, req, resp):
        """Handle POST requests."""
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Invalid JSON',
                                   'Could not decode the request body.')

        # Write user's code to file.
        code = result_json.get('code')
        if code:
            decoded_code = str(base64.b64decode(code), 'utf-8')
            code_filename = util.write_str_to_file(decoded_code)
        else:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Invalid JSON.', 'No code provided.')

        # Generate problem and compute solution.
        problem, _ = Problem1().generate()
        solution = Problem1().solve(problem)

        # Run user's code and verify their answer.
        answer = PythonRunner().run(code_filename, problem)
        solved = Problem1().verify(answer, solution)

        resp.status = falcon.HTTP_200
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = '{"success": true}' if solved else '{"success": false}'


app = falcon.API()
app.add_route('/submit', SubmitResource())
