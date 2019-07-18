import os
import time
import hashlib
import logging

from .simple_lxd import simple_lxd as lxd

logger = logging.getLogger(__name__)


def write_str_to_file(string, extension='', encoding='utf-8'):
    """
    Save the contents of a string to a file.

    :param string: the data to be saved
    :param extension: the file extension to be used for the file's name
    :returns the name of the file containing the string data
    """

    # Convert the code to a byte string.
    blob = string.encode(encoding)

    # Use the time so that two identical files have different file names
    time_bytes = bytes(str(time.time()), encoding=encoding)

    # Hash the byte string to generate a filename.
    m = hashlib.sha1()
    m.update(blob)
    m.update(time_bytes)
    hash_code = m.hexdigest()

    filename = "{}{}".format(hash_code, extension)

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
    if os.path.isfile(filename):
        logger.debug("Deleting file: {:s}".format(filename))
        os.remove(filename)


def configure_lxd() -> None:
    logger.debug("Configuring Linux container profile...")
    ll_profile = "lovelace"
    lxd.profile_delete(ll_profile)
    lxd.profile_copy("default", ll_profile)
    lxd.profile_set(ll_profile, "limits.cpu", "1")
    lxd.profile_set(ll_profile, "limits.cpu.allowance", "100%")
    lxd.profile_set(ll_profile, "limits.cpu.priority", "5")
    lxd.profile_set(ll_profile, "limits.disk.priority", "5")
    lxd.profile_set(ll_profile, "limits.memory", "750MB")
    lxd.profile_set(ll_profile, "limits.memory.enforce", "hard")
    lxd.profile_set(ll_profile, "limits.memory.swap", "false")
    lxd.profile_set(ll_profile, "limits.processes", "200")
    lxd.profile_set(ll_profile, "security.nesting", "false")
    lxd.profile_set(ll_profile, "security.privileged", "false")
    # lxd.profile_device_remove(ll_profile, "eth0")
