import base64
import json
import os
import unittest

import requests

class TestApi(unittest.TestCase):
    def test_all_problems(self):
        for solution_filename in os.listdir('../solutions/'):
            problem_name, extension = solution_filename.split(sep='.')
            language = {'py': 'python3', 'jl': 'julia'}.get(extension)
            with open('../solutions/' + solution_filename, 'r') as solution_file:
                code = solution_file.read()
            code_b64 = base64.b64encode(code.encode('utf-8')).decode('utf-8')
            payload_dict = {
                'problem': problem_name,
                'language': language,
                'code': code_b64,
            }
            payload_json = json.dumps(payload_dict)
            resp = requests.post('http://localhost:14714/submit', data=payload_json)
            resp_data = json.loads(resp.text)
            self.assertTrue(resp_data['success'], 'Failed when submitting good solution for {}\n{}'.format(problem_name, json.dumps(resp_data, indent=4)))

