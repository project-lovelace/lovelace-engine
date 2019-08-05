import os
import pickle
import subprocess

from ctypes import cdll, POINTER, c_int, c_double, c_bool, c_char_p, c_void_p

from numpy import array, ndarray, zeros
from numpy.ctypeslib import ndpointer

def infer_simple_ctype(var):
    if isinstance(var, int):
        return c_int

    elif isinstance(var, float):
        return c_double

    elif isinstance(var, bool):
        return c_bool

    elif isinstance(var, str):
        return c_char_p

    else:
        raise NotImplementedError("Cannot infer ctype of type(var)={:}, var={:}".format(type(var), var))

def preprocess_types(input_tuple, output_tuple):
    input_list = []
    arg_ctypes = []
    output_list = []

    for var in input_tuple:
        if isinstance(var, str):
            arg_ctypes.append(c_char_p)

            # C wants bytes, not strings.
            c_str = bytes(var, "utf-8")
            input_list.append(c_char_p(c_str))

        elif isinstance(var, list):
            if isinstance(var[0], (list, tuple)):
                raise NotImplementedError(f"Cannot infer ctype of a list containing lists or tuples: var={var}")

            arr_ctype = infer_simple_ctype(var[0]) * len(var)
            arg_ctypes.append(arr_ctype)

            arr = arr_ctype(*var)
            input_list.append(arr)

            # For a Python list, we add an extra argument for the size of the C array.
            arg_ctypes.append(c_int)
            input_list.append(len(var))

        elif isinstance(var, ndarray):
            arr_ctype = ndpointer(dtype=var.dtype, flags="C_CONTIGUOUS")
            arg_ctypes.append(arr_ctype)
            input_list.append(var)

            # For a numpy ndarray, we add extra arguments for each dimension size of the input C array.
            for s in var.shape:
                arg_ctypes.append(c_int)
                input_list.append(s)

        else:
            arg_ctypes.append(infer_simple_ctype(var))
            input_list.append(var)

    if len(output_tuple) == 1:
        rvar = output_tuple[0]  # Return variable

        if isinstance(rvar, list):
            # If the C function needs to return an array, Python must allocate memory for the array and pass it to the
            # C function. So we add an extra argument for a pointer to the pre-allocated C array and set the return type
            # to void.
            if isinstance(rvar[0], (list, tuple)):
                raise NotImplementedError(f"Cannot infer ctype of a list containing lists or tuples: var={var}")

            arr = array(rvar)

            arr_ctype = ndpointer(dtype=arr.dtype, flags="C_CONTIGUOUS")
            arg_ctypes.append(arr_ctype)

            input_list.append(arr)

            res_ctype = c_void_p

            output_list.append(arr)

            output_list.append(arr)

        elif isinstance(rvar, ndarray):
            arr_ctype = ndpointer(dtype=rvar.dtype, flags="C_CONTIGUOUS")
            arg_ctypes.append(arr_ctype)

            arr = zeros(rvar.shape, dtype=rvar.dtype)
            input_list.append(arr)

            res_ctype = c_void_p

            output_list.append(arr)
        else:
            res_ctype = infer_simple_ctype(rvar)

    else:
        # In the case of multiple return types, we add extra input arguments (one pointer per each return variable)
        # and the C function will mutate the values pointed to by the pointers. These arguments will always be at
        # the very end of the argument list.
        for var in output_tuple:
            type = infer_simple_ctype(var)
            ptype = POINTER(type)

            arg_ctypes.append(ptype)

            val = type()  # Create a value, e.g. c_int or c_double, that will be mutated by the C function.
            input_list.append(val)
            output_list.append(val)

        res_ctype = c_void_p

    return arg_ctypes, res_ctype, input_list, output_list

def ctype_output(var):
    if isinstance(var, (c_int, c_double)):
        return var.value
    elif isinstance(var, bytes):
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
_lib = cdll.LoadLibrary(os.path.join(cwd, lib_file))

for i, (input_tuple, correct_output_tuple) in enumerate(zip(input_tuples, correct_output_tuples)):
    # Use the input and output tuple to infer the type of input arguments and return value. We do this again for each
    # test case in case outputs change type or arrays change size.
    arg_ctypes, res_ctype, ctyped_input_list, output_list = preprocess_types(input_tuple, correct_output_tuple)

    _lib.$FUNCTION_NAME.argtypes = arg_ctypes
    _lib.$FUNCTION_NAME.restype = res_ctype

    # $FUNCTION_NAME will be replaced by the name of the user's function by the CodeRunner before this script is run.
    user_output = _lib.$FUNCTION_NAME(*ctyped_input_list)

    # If the C function returns nothing, then it must have mutated some of its input arguments.
    # We'll pull them out here.
    if res_ctype == c_void_p:
        user_output = []
        for var in output_list:
            user_output.append(ctype_output(var))
        user_output = tuple(user_output)
    else:
        user_output = ctype_output(user_output)

    output_dict = {
        'user_output': user_output if isinstance(user_output, tuple) else (user_output,),
        'runtime': 0,
        'max_mem_usage': 0
    }

    output_pickle = '{:s}.output{:d}.pickle'.format(run_id, i)
    with open(output_pickle, mode='wb') as f:
        pickle.dump(output_dict, file=f, protocol=pickle.HIGHEST_PROTOCOL)
