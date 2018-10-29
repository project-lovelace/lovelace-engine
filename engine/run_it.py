import importlib
import os
import pickle
import time
import tracemalloc

# os.chdir('/tmp')
run_id = os.path.basename(__file__).split('.')[0]

input_pickle = '{}.input.pickle'.format(run_id)
output_pickle = '{}.output.pickle'.format(run_id)

user_module = importlib.import_module(run_id)
with open(input_pickle, mode='rb') as f:
    input_params = pickle.load(f)

tracemalloc.start()
t1 = time.time()

user_output = user_module.$FUNCTION_NAME(*input_params)

t2 = time.time()
_, max_mem_usage = tracemalloc.get_traced_memory()
tracemalloc.stop()

user_output = (user_output,) if type(user_output) is not tuple else user_output
runtime = t2 - t1

output_dict = {
    'user_output': user_output,
    'runtime': runtime,
    'max_mem_usage': max_mem_usage
    }

with open(output_pickle, mode='wb') as f:
    pickle.dump(output_dict, file=f)
