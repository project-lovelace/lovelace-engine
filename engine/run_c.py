import os
import ctypes
import pickle
import subprocess

def infer_argtypes(input_tuple):
    arg_ctypes = []
    for var in input_tuple:
        if isinstance(var, int):
            arg_ctypes.append(ctypes.c_int)
        elif isinstance(var, float):
            arg_ctypes.append(ctypes.c_double)
        elif isinstance(var, str):
            arg_ctypes.append(ctypes.c_char_p)

    return arg_ctypes

run_id = os.path.basename(__file__).split('.')[0]
input_pickle = "{:s}.input.pickle".format(run_id)
code_file = "{:s}.c".format(run_id)
lib_file = "{:s}.so".format(run_id)

with open(input_pickle, mode='rb') as f:
    input_tuples = pickle.load(f)

# Compile the user's C code.
# -fPIC for position-independent code, needed for shared libraries to work no matter where in memory they are loaded.
# check=True will raise a CalledProcessError for non-zero return codes (user code failed to compile.)
subprocess.run(["gcc", "-fPIC", "-shared", "-o", lib_file, code_file], check=True)

# Load the compiled shared library. We use the absolute path as the cwd is not in LD_LIBRARY_PATH so cdll won't find
# the .so file if we use a relative path or just a filename.
cwd = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(cwd, lib_file))

# Use the first input tuple to infer the type of input arguments.
lib.$FUNCTION_NAME.argtypes = infer_argtypes(input_tuples[0])

lib.$FUNCTION_NAME.restype = ctypes.c_double

for i, input_tuple in enumerate(input_tuples):
    # $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner before this script is run.
    user_output = lib.$FUNCTION_NAME(*input_tuple)

    output_dict = {
        'user_output': user_output if isinstance(user_output, tuple) else (user_output,),
        'runtime': 0,
        'max_mem_usage': 0
    }

    output_pickle = '{:s}.output{:d}.pickle'.format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
