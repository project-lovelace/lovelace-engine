import importlib
import json
import os
import pickle
import subprocess
import time
import tracemalloc

run_id = os.path.basename(__file__).split('.')[0]

code_file = '{}.js'.format(run_id)
input_pickle = '{}.input.pickle'.format(run_id)
input_json = '{}.input.json'.format(run_id)
output_pickle = '{}.output.pickle'.format(run_id)
output_json = '{}.output.json'.format(run_id)

with open(input_pickle, mode='rb') as f:
    input_params = pickle.load(f)

func_call_str = '$FUNCTION_NAME(' + ', '.join([json.dumps(param) for param in params]) + ')'

glue_code = """
let user_output = {}
const fs = require('fs');
let data = JSON.stringify(user_output);
fs.writeFileSync('{}', data);
""".format(func_call_str, output_json)

with open(code_file, mode='a') as f:
	f.write(glue_code)

subprocess.run(['node', code_file])

with open(output_json, mode='r') as f:
	user_output = json.loads(f.read())

user_output = tuple(user_output) if type(user_output) is list else (user_output,)
runtime = 999  # TODO: get runtime from the user's file
max_mem_usage = 999999

output_dict = {
    'user_output': user_output,
    'runtime': runtime,
    'max_mem_usage': max_mem_usage
}

with open(output_pickle, mode='wb') as f:
    pickle.dump(output_dict, file=f)
