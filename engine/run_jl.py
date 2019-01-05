import julia
import os
import pickle

run_id = os.path.basename(__file__).split('.')[0]

input_pickle = '{}.input.pickle'.format(run_id)
output_pickle = '{}.output.pickle'.format(run_id)

with open(input_pickle, mode='rb') as f:
    input_params = pickle.load(f)

j = julia.Julia()
j.include("julia_runner_util.jl")

j.timed_function_call(j.$FUNCTION_NAME, input_params)  # Call function to pre/compile.
julia_run = j.timed_function_call(j.$FUNCTION_NAME, user_input)

user_output = julia_run[0]
runtime = julia_run[1]
bytes_allocated = julia_run[2]
max_mem_usage = bytes_allocated / 1024

user_output = user_output if type(user_output) is tuple else (user_output,)

# print("User input: {:}".format(user_input))
# print("User output: {:}".format(user_output))
# print("Runtime: {:} seconds".format(runtime))
# print("Memory allocated: {:} bytes".format(bytes_allocated))

submission_data = {
    'user_output': user_output,
    'runtime': runtime,
    'max_mem_usage': max_mem_usage,
}

with open(output_pickle, mode='wb') as f:
    pickle.dump(submission_data, file=f)
