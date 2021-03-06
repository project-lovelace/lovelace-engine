import os
import pickle
import subprocess

from ctypes import cdll, POINTER, c_int, c_double, c_bool, c_char_p, c_void_p

from numpy import array, ndarray, zeros, arange, issubdtype, integer, uintp, intc
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

            elem_ctype = infer_simple_ctype(var[0])
            arr_ctype = elem_ctype * len(var)
            arg_ctypes.append(arr_ctype)

            if elem_ctype == c_char_p:
                var = [bytes(s, "utf-8") for s in var]

            arr = arr_ctype(*var)
            input_list.append(arr)

            # For a Python list, we add an extra argument for the size of the C array.
            arg_ctypes.append(c_int)
            input_list.append(len(var))

        elif isinstance(var, ndarray):
            if issubdtype(var.dtype, integer):
                var = var.astype(intc)

            if len(var.shape) == 1:
                arr_ctype = ndpointer(dtype=var.dtype, ndim=len(var.shape), shape=var.shape, flags="C_CONTIGUOUS")
                arg_ctypes.append(arr_ctype)
                input_list.append(var)

            elif len(var.shape) == 2:
                # If the numpy ndarray is two-dimensional then we want to pass in an array of pointers of type uintp
                # which corresponds to a double** type. This enables the C function to index into the array as if it
                # were a 2D array, e.g. like arr[i][j]. We could pass it in as we do for the 1D case but then the C
                # function would be restricted to indexing the array linearly, e.g. arr[i].
                var_pp = (var.ctypes.data + arange(var.shape[0]) * var.strides[0]).astype(uintp)
                var_ptr_t = ndpointer(dtype=uintp)

                arg_ctypes.append(var_ptr_t)
                input_list.append(var_pp)

            else:
                raise NotImplementedError("Cannot preprocess input numpy ndarray of shape {:}".format(var.shape))

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

            arr_ctype = ndpointer(dtype=arr.dtype, ndim=len(arr.shape), shape=arr.shape, flags="C_CONTIGUOUS")
            arg_ctypes.append(arr_ctype)

            input_list.append(arr)

            res_ctype = c_void_p

            output_list.append(arr)

        elif isinstance(rvar, ndarray):
            new_dtype = intc if issubdtype(rvar.dtype, integer) else rvar.dtype

            if len(rvar.shape) == 1:
                arr_ctype = ndpointer(dtype=new_dtype, ndim=len(rvar.shape), shape=rvar.shape, flags="C_CONTIGUOUS")
                arr = zeros(rvar.shape, dtype=new_dtype)

                arg_ctypes.append(arr_ctype)
                input_list.append(arr)
                output_list.append(arr)

            elif len(rvar.shape) == 2:
                arr = zeros(rvar.shape, dtype=new_dtype)
                arr_pp = (arr.ctypes.data + arange(arr.shape[0]) * arr.strides[0]).astype(uintp)
                arr_ptr_t = ndpointer(dtype=uintp)

                arg_ctypes.append(arr_ptr_t)
                input_list.append(arr_pp)
                output_list.append(arr)

            else:
                raise NotImplementedError("Cannot preprocess output numpy ndarray of shape {:}".format(rvar.shape))

            res_ctype = c_void_p

        else:
            res_ctype = infer_simple_ctype(rvar)

    else:
        # In the case of multiple return types, we add extra input arguments (one pointer per each return variable)
        # and the C function will mutate the values pointed to by the pointers. These arguments will always be at
        # the very end of the argument list. The return type is set to void.
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
    elif isinstance(var, ndarray):
        return var.tolist()
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
