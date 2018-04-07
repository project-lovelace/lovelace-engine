import importlib
import os
import pickle

os.chdir('/tmp')
run_id = os.path.basename(__file__).split('.')[0]

input_pickle = '{}.input.pickle'.format(run_id)
output_pickle = '{}.output.pickle'.format(run_id)

user_module = importlib.import_module(run_id)
with open(input_pickle, mode='rb') as f:
    input_params = pickle.load(f)

user_output = user_module.solution(*input_params)
user_output = (user_output,) if type(user_output) is not tuple else user_output
with open(output_pickle, mode='wb') as f:
    pickle.dump(user_output, file=f)
