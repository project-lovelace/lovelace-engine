import json
import os
import pickle
import subprocess

run_id = os.path.basename(__file__).split('.')[0]

code_file = '{}.js'.format(run_id)
input_pickle = '{}.input.pickle'.format(run_id)
input_json = '{}.input.json'.format(run_id)
output_pickle = '{}.output.pickle'.format(run_id)
output_json = '{}.output.json'.format(run_id)

with open(input_pickle, mode='rb') as f:
    params = pickle.load(f)

func_call_str = '$FUNCTION_NAME(' + ', '.join([json.dumps(param) for param in params]) + ')'

glue_code = """
const timeStart = process.hrtime();
let userOutput = {};
const timeDiff = process.hrtime(timeStart);
const runTime = timeDiff[0] + (timeDiff[1] / 1e9);

const maxMemoryUsage = 0;

const submissionData = {{ 
  "userOutput": userOutput,
  "runTime": runTime,
  "maxMemoryUsage": maxMemoryUsage
}};  // Double braces to avoid interfering with Python brace-based string formatting.

const fs = require('fs');
let data = JSON.stringify(submissionData);
fs.writeFileSync('{}', data);
""".format(func_call_str, output_json)

with open(code_file, mode='a') as f:
    f.write(glue_code)

subprocess.run(['node', code_file])

with open(output_json, mode='r') as f:
    submission_data = json.loads(f.read())

user_output = submission_data['userOutput']
runtime = submission_data['runTime']
max_mem_usage = submission_data['maxMemoryUsage']

if type(user_output) is list \
        and len(user_output) == 1 \
        and user_output[0] is list:
    user_output = (user_output[0],)  # Solution is a list
elif type(user_output) is list:
    user_output = tuple(user_output)  # Solution is a "multiple return"
else:
    user_output = (user_output,)  # Solution is a string or number

output_dict = {
    'user_output': user_output,
    'runtime': runtime,
    'max_mem_usage': max_mem_usage,
}

with open(output_pickle, mode='wb') as f:
    pickle.dump(output_dict, file=f)
