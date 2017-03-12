import falcon
import json

from problems.problem1 import Problem1
from runners.python_runner import PythonRunner
import util


class SubmitResource(object):

    def on_post(self, req, resp):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Invalid JSON', 'Could not decode the request body.')

        # Write user's code to file.
        code = result_json['submitted_code']
        code_filename = util.write_str_to_file(code)

        # Generate problem and save the inputs to file.
        problem, solution = Problem1().generate()
        # input_filename = util.write_list_to_file(problem)

        # Run user's code and verify their answer.
        answer = PythonRunner().run(code_filename, problem)
        solved = Problem1().verify(answer, solution)

        print(solved)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result_json)


# Let's initialize a callable WSGI app here
app = falcon.API()

# Instantiate our resource - in general, resources are represented by long-lived class instances
submit = SubmitResource()

# Let 'things' handle all requests to the '/things' URL path
app.add_route('/submit', submit)
