import json
import unittest

import requests

class TestApi(unittest.TestCase):
    def test_rocket_science(self):
        payload_dict = {
            'problem': 'rocket-science',
            'language': 'python3',
            'code': 'aW1wb3J0IG1hdGgKCnZfZSA9IDI1NTAgICMgcm9ja2V0IGV4aGF1c3QgdmVsb2NpdHkgW20vc10KTSA9IDI1MDAwMCAgIyByb2NrZXQgZHJ5IG1hc3MgW2tnXQoKZGVmIHJvY2tldF9mdWVsKHYpOgogICAgcmV0dXJuIE0gKiAobWF0aC5leHAodiAvIHZfZSkgLSAxKQ==',
        }
        payload_json = json.dumps(payload_dict)
        resp = requests.post('http://localhost:14714/submit', data=payload_json)
        resp_data = json.loads(resp.text)
        self.assertTrue(resp_data['success'])

