import os
import ctypes
import pickle
import subprocess

from numpy import ndarray
from numpy.ctypeslib import as_ctypes_type, as_ctypes, as_array

def infer_ctype(var):
    if isinstance(var, int):
        return ctypes.c_int

    elif isinstance(var, float):
        return ctypes.c_double

    elif isinstance(var, bool):
        return ctypes.c_bool

    elif isinstance(var, str):
        return ctypes.c_char_p

    else:
        raise NotImplementedError("Cannot infer ctype of type(var)={:}, var={:}".format(type(var), var))

def infer_arg_and_res_types(input_tuple, output_tuple):
    if len(output_tuple) > 1:
        raise NotImplementedError("C does not support multiple return values but len(output_tuple)={:d}"
                                  .format(len(output_tuple)))

    arg_ctypes = []
    for var in input_tuple:
        if isinstance(var, list):
            if isinstance(var[0], (list, tuple)):
                raise NotImplementedError(f"Cannot infer ctype of a list containing lists or tuples: var={var}")

            arr_ctype = infer_ctype(var[0]) * len(var)
            arg_ctypes.append(arr_ctype)

            # For a Python list, we add an extra argument for the size of the C array.
            arg_ctypes.append(ctypes.c_int)

        elif isinstance(var, ndarray):
            arr_ctype = type(as_ctypes(var))
            arg_ctypes.append(arr_ctype)

            # For a numpy ndarray, we add extra arguments for each dimension size of the input C array.
            for _ in range(len(var.shape)):
                arg_ctypes.append(ctypes.c_int)

        else:
            arg_ctypes.append(infer_ctype(var))

    rvar = output_tuple[0]  # Return variable.
    if isinstance(rvar, list):
        arr_ctype = infer_ctype(rvar[0]) * len(rvar)
        arg_ctypes.append(arr_ctype)
        res_ctype = ctypes.c_void_p
    else:
        res_ctype = infer_ctype(rvar)

    return arg_ctypes, res_ctype

def ctype_input_list(input_tuple):
    input_list = []
    for k, var in enumerate(input_tuple):
        if isinstance(var, str):
            # C wants bytes, not strings.
            input_list.append(ctypes.c_char_p(bytes(var, "utf-8")))

        elif isinstance(var, list):
            # For a list, we add an extra argument for the size of the input C array.
            array_type = infer_ctype(var[0]) * len(var)
            arr = array_type(*var)
            input_list.append(arr)
            input_list.append(len(var))

        elif isinstance(var, ndarray):
            # For an array, we add extra arguments for the size of the input C array (one extra argument per dimension).
            arr = as_ctypes(var)
            input_list.append(arr)
            for s in var.shape:
                input_list.append(s)

        else:
            input_list.append(var)

    return input_list

def ctype_output(var, correct_output):
    if isinstance(correct_output, str):
        if not isinstance(var, bytes):
            raise TypeError("Return type is wrong! Was expecting return type char* (Python bytes). "
                            "Instead got return type {:}".format(type(var)))
        return var.decode("utf-8")
    else:
        return var

run_id = os.path.basename(__file__).split('.')[0]
input_pickle = "{:s}.input.pickle".format(run_id)
correct_pickle = "{:s}.correct.pickle".format(run_id)
code_file = "{:s}.c".format(run_id)
lib_file = "{:s}.so".format(run_id)

with open(input_pickle, mode='rb') as f:
    input_tuples = pickle.load(f)

with open(correct_pickle, mode='rb') as f:
    correct_output_tuples = pickle.load(f)

# Compile the user's C code.
# -fPIC for position-independent code, needed for shared libraries to work no matter where in memory they are loaded.
# check=True will raise a CalledProcessError for non-zero return codes (user code failed to compile.)
subprocess.run(["gcc", "-fPIC", "-shared", "-o", lib_file, code_file], check=True)

# Load the compiled shared library. We use the absolute path as the cwd is not in LD_LIBRARY_PATH so cdll won't find
# the .so file if we use a relative path or just a filename.
cwd = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.cdll.LoadLibrary(os.path.join(cwd, lib_file))

for i, (input_tuple, correct_output_tuple) in enumerate(zip(input_tuples, correct_output_tuples)):
    # Use the input and output tuple to infer the type of input arguments and return value. We do this again for each
    # test case in case outputs change type or arrays change size.
    arg_ctypes, res_ctype = infer_arg_and_res_types(input_tuple, correct_output_tuple)
    lib.$FUNCTION_NAME.argtypes = arg_ctypes
    lib.$FUNCTION_NAME.restype = res_ctype

    ctyped_input_list = ctype_input_list(input_tuple)

    # $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner before this script is run.
    user_output = lib.$FUNCTION_NAME(*ctyped_input_list)

    user_output = ctype_output(user_output, correct_output_tuple[0])

    output_dict = {
        'user_output': user_output if isinstance(user_output, tuple) else (user_output,),
        'runtime': 0,
        'max_mem_usage': 0
    }

    output_pickle = '{:s}.output{:d}.pickle'.format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
