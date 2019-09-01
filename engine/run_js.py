import os
import json
import pickle
import subprocess

run_id = os.path.basename(__file__).split('.')[0]
input_pickle = "{:s}.input.pickle".format(run_id)
code_file = "{:s}.js".format(run_id)

with open(input_pickle, mode='rb') as f:
    input_tuples = pickle.load(f)

for i, input_tuple in enumerate(input_tuples):
    output_json = "{:s}.output{:d}.json".format(run_id, i)

    # $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner
    # before this script is run.
    func_call_str = "$FUNCTION_NAME(" + ", ".join([json.dumps(arg) for arg in input_tuple]) + ")"

    glue_code = """
    var timeStart = process.hrtime();
    var userOutput = {:s};
    var timeDiff = process.hrtime(timeStart);
    var runTime = timeDiff[0] + (timeDiff[1] / 1e9);
    
    var maxMemoryUsage = 0;
    
    var submissionData = {{ 
      "userOutput": userOutput,
      "runTime": runTime,
      "maxMemoryUsage": maxMemoryUsage
    }};  // Double braces to avoid interfering with Python brace-based string formatting.
    
    var fs = require('fs');
    var data = JSON.stringify(submissionData);
    fs.writeFileSync('{:s}', data);
    """.format(func_call_str, output_json)

    # This will append glue code to the code file for each test case.
    with open(code_file, mode='a') as f:
        f.write(glue_code)

# Run all test cases at the same time so we only run `node` once.
subprocess.run(["node", code_file])

for i, _ in enumerate(input_tuples):
    output_json = "{:s}.output{:d}.json".format(run_id, i)
    with open(output_json, mode='r') as f:
        submission_data = json.loads(f.read())

    user_output = submission_data['userOutput']
    runtime = submission_data['runTime']
    max_mem_usage = submission_data['maxMemoryUsage']

    if isinstance(user_output, list) and len(user_output) == 1 and isinstance(user_output[0], list):
        user_output = (user_output[0],)  # Solution is a list
    elif isinstance(user_output, list):
        user_output = tuple(user_output)  # Solution is a "multiple return"
    else:
        user_output = (user_output,)  # Solution is a string or number

    output_dict = {
        'user_output': user_output,
        'runtime': runtime,
        'max_mem_usage': max_mem_usage,
    }

    output_pickle = "{:s}.output{:d}.pickle".format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
