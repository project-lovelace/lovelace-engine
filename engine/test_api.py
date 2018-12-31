import base64
import json
import os
import unittest

import requests


class TestApi(unittest.TestCase):
    solutions_dir = '../solutions/'

    def submit_solution(self, file_name):
        solution_file_path = os.path.join(self.solutions_dir, file_name)
        with open(solution_file_path, 'r') as solution_file:
            code = solution_file.read()
        code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')

        problem_name, extension = file_name.split(sep='.')
        language = {'py': 'python3', 'jl': 'julia', 'js': 'javascript'}.get(extension)

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
        for file_name in os.listdir(self.solutions_dir):
            if file_name.split('.')[1] == 'js':
                pass
            print('Submitting {}!'.format(file_name))
            result = self.submit_solution(file_name)
            self.assertTrue(result['success'], 'Failed. Engine output:\n{}'.format(json.dumps(result, indent=4)))

    def test_all_problems_javascript_success(self):
        file_name = 'rocket-science.js'
        print('Submitting {}!'.format(file_name))
        result = self.submit_solution(file_name)
        self.assertTrue(result['success'], 'Failed. Engine output:\n{}'.format(json.dumps(result, indent=4)))
