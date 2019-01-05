import base64
import json
import os
import unittest

import requests


class TestApi(unittest.TestCase):
    solutions_dir = '../solutions/'
    python_solutions_dir = os.path.join(solutions_dir, 'python')
    javascript_solutions_dir = os.path.join(solutions_dir, 'javascript')
    julia_solutions_dir = os.path.join(solutions_dir, 'julia')

    def submit_solution(self, file_path):
        with open(file_path, 'r') as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')

        problem_name, extension = os.path.basename(file_path).split(sep='.')
        language = {'py': 'python', 'jl': 'julia', 'js': 'javascript'}.get(extension)

        payload_dict = {
            'problem': problem_name,
            'language': language,
            'code': code_b64,
        }
        payload_json = json.dumps(payload_dict)

        response = requests.post('http://localhost:14714/submit', data=payload_json)
        response_data = json.loads(response.text)

        return response_data

    def test_all_problems_python_success(self):
        for file_name in os.listdir(self.python_solutions_dir):
            file_path = os.path.join(self.python_solutions_dir, file_name)
            print('Submitting {}!'.format(file_path))
            result = self.submit_solution(file_path)
            self.assertTrue(result['success'], 'Failed. Engine output:\n{}'.format(json.dumps(result, indent=4)))

    def test_all_problems_javascript_success(self):
        for file_name in os.listdir(self.javascript_solutions_dir):
            file_path = os.path.join(self.javascript_solutions_dir, file_name)
            print('Submitting {}!'.format(file_path))
            result = self.submit_solution(file_path)
            self.assertTrue(result['success'], 'Failed. Engine output:\n{}'.format(json.dumps(result, indent=4)))

    def test_all_problems_julia_success(self):
        for file_name in os.listdir(self.julia_solutions_dir):
            file_path = os.path.join(self.julia_solutions_dir, file_name)
            print('Submitting {}!'.format(file_path))
            result = self.submit_solution(file_path)
            self.assertTrue(result['success'], 'Failed. Engine output:\n{}'.format(json.dumps(result, indent=4)))
