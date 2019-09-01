import os
import time
import pickle
import importlib
import tracemalloc

run_id = os.path.basename(__file__).split('.')[0]
input_pickle = '{:s}.input.pickle'.format(run_id)

user_module = importlib.import_module(run_id)

with open(input_pickle, mode='rb') as f:
    input_tuples = pickle.load(f)

for i, input_tuple in enumerate(input_tuples):
    tracemalloc.start()
    t1 = time.time()

    # $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner before this script is run.
    user_output = user_module.$FUNCTION_NAME(*input_tuple)

    t2 = time.time()
    _, max_mem_usage = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    user_output = user_output if isinstance(user_output, tuple) else (user_output,)
    runtime = t2 - t1

    output_dict = {
        'user_output': user_output,
        'runtime': runtime,
        'max_mem_usage': max_mem_usage
        }

    output_pickle = '{:s}.output{:d}.pickle'.format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
