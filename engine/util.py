# util.py

import os
import hashlib


def write_str_to_file(string):
    """Saves a string to a file and returns the filename."""

    # Convert the code to a byte string.
    blob = string.encode('utf-8')

    # Hash the byte string to generate a filename.
    m = hashlib.sha1()
    m.update(blob)
    hash_code = m.hexdigest()

    filename = "{}.py".format(hash_code)

    f = open(filename, 'w')
    f.write(string)
    f.close()

    return filename


def write_list_to_file(the_list):
    """Saves a list to a file and returns the filename."""

    string = ' '.join(the_list)
    filename = write_str_to_file(string)

    return filename


def read_str_from_file(filename):
    f = open(filename, 'r')
    file_contents = f.read()
    f.close()

    return file_contents


def read_list_from_file(filename):
    file_contents = read_str_from_file(filename)
    the_list = file_contents.split(sep=' ')

    return the_list


def delete_file(filename):
    os.remove(filename)
    return
