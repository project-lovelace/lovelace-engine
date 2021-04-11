import os
import json
import pickle
import subprocess

run_id = os.path.basename(__file__).split('.')[0]
input_json = '{:s}.input.json'.format(run_id)
code_file = '{:s}.jl'.format(run_id)

glue_code = '''
import JSON

timed_function_call(f, input) = @timed f(input...)

function json_array_dim(a)
    if length(size(a)) > 0
        return 1 + json_array_dim(a[1])
    else
        return 0
    end
end

function json_array_eltype(a)
    if eltype(a) == Any
        return json_array_eltype(a[1])
    else
        return eltype(a)
    end
end

juliafy_json(t) = t
juliafy_json(a::Array) = convert(Array{{json_array_eltype(a), json_array_dim(a)}}, hcat(a...))

tupleit(t) = tuple(t)
tupleit(t::Tuple) = t

input_tuples = JSON.Parser.parsefile("{:s}")

for (i, input_tuple) in enumerate(input_tuples)

    input_tuple = [juliafy_json(elem) for elem in input_tuple]

    output_tuple = $FUNCTION_NAME(input_tuple...) |> tupleit

    open("{:s}.output$i.json", "w") do f
       JSON.print(f, output_tuple)
    end
end
'''.format(input_json, run_id)

# This will append glue code to the code file to run the test cases.
with open(code_file, mode='a') as f:
    f.write(glue_code)

subprocess.run(["julia", code_file])

with open(input_json, mode='rb') as f:
    input_tuples = json.load(f)

for i, _ in enumerate(input_tuples):
    output_json = "{:s}.output{:d}.json".format(run_id, i+1)

    with open(output_json, mode='r') as f:
        user_output = json.loads(f.read())

    if isinstance(user_output, list) and len(user_output) == 1 and isinstance(user_output[0], list):
        user_output = (user_output[0],)  # Solution is a list
    elif isinstance(user_output, list):
        user_output = tuple(user_output)  # Solution is a "multiple return"
    else:
        user_output = (user_output,)  # Solution is a string or number

    user_output = user_output if isinstance(user_output, tuple) else (user_output,)

    output_dict = {
        'user_output': user_output,
        'runtime': 0,
        'max_mem_usage': 0,
    }

    output_pickle = "{:s}.output{:d}.pickle".format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
