import julia
import os
import pickle

run_id = os.path.basename(__file__).split('.')[0]
input_pickle = '{:s}.input.pickle'.format(run_id)
code_file = '{:s}.jl'.format(run_id)

j = julia.Julia()
j.include("julia_runner_util.jl")
j.include(code_file)

with open(input_pickle, mode='rb') as f:
    input_tuples = pickle.load(f)

for i, input_tuple in enumerate(input_tuples):
    output_pickle = '{:s}.output{:d}.pickle'.format(run_id, i)

    if i == 0:
        # Call function to pre/compile. We need to do this if we want accurate performance statistics for the first
        # test case. $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner
        # before this script is run.
        j.timed_function_call(j.$FUNCTION_NAME, input_tuple)

    julia_run = j.timed_function_call(j.$FUNCTION_NAME, input_tuple)

    user_output = julia_run[0]
    runtime = julia_run[1]
    bytes_allocated = julia_run[2]
    max_mem_usage = bytes_allocated / 1024

    user_output = user_output if isinstance(user_output, tuple) else (user_output,)

    output_dict = {
        'user_output': user_output,
        'runtime': runtime,
        'max_mem_usage': max_mem_usage,
    }

    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
