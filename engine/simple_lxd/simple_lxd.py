import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import logging

logger = logging.getLogger(__name__)


class LXDError(Exception):
    pass


def launch(image, name, ephemeral=False, profile=None, config=None, instance_type=None):
    """
    Create and start containers from images.

    Syntax: lxc launch [<remote>:]<image> [<remote>:][<name>] [--ephemeral|-e]
        [--profile|-p <profile>...] [--config|-c <key=value>...]
        [--type|-t <instance type>]
    """
    logger.debug("Launching Linux container (image={:s}, name={:s}, ephemeral={:}, profile={:}, config={:}, "
                 "instance_type={:})...".format(image, name, ephemeral, profile, config, instance_type))

    command = ["lxc", "launch", image, name]

    if ephemeral:
        command.append("--ephemeral")
    if profile:
        command.append("--profile")
        command.append(profile)
    if config:
        command.append("--config")
        command.append(config)
    if instance_type:
        command.append("--type")
        command.append(instance_type)

    return _run(command)


def file_pull(container, source_path, target_path):
    """
    Pull files from containers.

    Syntax: lxc file pull [<remote>:]<container>/<path>
        [[<remote>:]<container>/<path>...] <target path>
    """
    logger.debug("Pulling file {:s} from Linux container {:s} to {:s}...".format(source_path, container, target_path))

    command = ["lxc", "file", "pull"]
    from_path = os.path.join(container, source_path)
    command.append(container + from_path)
    command.append(target_path)
    return _run(command)


def file_push(container, source_path, target_path, uid=None, gid=None, mode=None):
    """
    Push files into containers.

    Syntax: lxc file push [--uid=UID] [--gid=GID] [--mode=MODE] <source path>
        [<source path>...] [<remote>:]<container>/<path>
    """
    logger.debug("Pushing file {:s} into Linux container {:s} in {:s} (uid={:}, gid={:}, mode={:})..."
                 .format(source_path, container, target_path, uid, gid, mode))

    command = ["lxc", "file", "push", "--verbose"]
    # command = ["lxc", "file", "push", "--debug", "--verbose"]

    if uid:
        command.append("--uid=")
        command.append(uid)
    if gid:
        command.append("--gid=")
        command.append(gid)
    if mode:
        command.append("--mode=")
        command.append(mode)

    command.append(source_path)
    command.append(container + target_path)

    return _run(command)


def stop(container, log=True):
    """
    Stop running containers.

    Syntax: lxc stop [<remote>:]<container> [[<remote>:]<container>...]
    """

    logger.debug("Stopping Linux container {:s}...".format(container))

    command = ["lxc", "stop"]

    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)

    return _run(command, log=log)


def delete(container, log=True):
    """
    Delete containers and snapshots.

    Syntax: lxc delete [<remote>:]<container>[/<snapshot>]
        [[<remote>:]<container>[/<snapshot>]...]
    """
    logger.debug("Deleting Linux container {:s}...".format(container))

    command = ["lxc", "delete"]

    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)

    return _run(command, log=log)


def execute(container, command_line, mode="non-interactive", env=None):
    """
    Execute commands in containers.

    Syntax: lxc exec [<remote>:]<container>
        [--mode=auto|interactive|non-interactive] [--env KEY=VALUE...]
        [--] <command line>
    """
    logger.debug("Executing command `{:}` in Linux container {:s} (mode={:}, env={:})..."
                 .format(command_line, container, mode, env))

    command = ["lxc", "exec", container, "--mode={}".format(mode)]
    # command = ["lxc", "exec", "--verbose", "--debug", container, "--mode={}".format(mode)]

    if env:
        command.append("--env")
        command.append(env)

    command.append("--")
    command.extend(command_line)

    return _run(command, timeout=60)


def profile_create(name, remote=None):
    """
    Create a new profile.

    Syntax: lxc profile create [<remote>:]<profile>
    """
    logger.debug("Creating Linux container profile {:} (remote={:})...".format(name))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "create", profile]
    return _run(command)


def profile_copy(src_name, dst_name, src_remote=None, dst_remote=None):
    """
    Copy the profile.

    Syntax: lxc profile copy [<remote>:]<profile> [<remote>:]<profile>
    """
    logger.debug("Copying Linux container profile {:s} to {:s} (src_remote={:}, dst_remote={:})..."
                 .format(src_name, dst_name, src_remote, dst_remote))

    src = "{}:{}".format(src_remote, src_name) if src_remote else src_name
    dst = "{}:{}".format(dst_remote, dst_name) if dst_remote else dst_name

    command = ["lxc", "profile", "copy", src, dst]
    return _run(command)


def profile_set(name, key, value, remote=None):
    """
    Set profile configuration.

    Syntax: lxc profile set [<remote>:]<profile> <key> <value>
    """
    logger.debug("Setting Linux container profile {:s} (key={:}, value={:}, remote={:})..."
                 .format(name, key, value, remote))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "set", profile, key, value]
    return _run(command)


def profile_delete(name, remote=None):
    """
    Delete a profile.

    Syntax: lxc profile delete [<remote>:]<profile>
    """
    logger.debug("Deleting Linux container profile {:s} (remote={:})...".format(name, remote))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "delete", profile]
    return _run(command)


def profile_device_remove(name, device, remote=None):
    """
    Remove a device from a profile.

    Syntax: lxc profile device remove [<remote>:]<profile> <name>
    """
    logger.debug("Deleting device {:s} from profile {:s} (remote={:})...".format(device, name, remote))

    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "device", "remove", profile, device]
    return _run(command)


def _run(command_args, timeout=60, log=True):
    # We have a flag for logging because the API destructor calls lxd stop and lxd delete, which may
    # be called at the same time as other stuff shuttind down and typically the logging module is
    # shut down before we can stop and delete the containers so by setting log=False we can still
    # stop and delete the containers from a destructor.
    if log:
        logger.debug("Running command (timeout={:d}): {:s}".format(timeout, " ".join(command_args)))

    max_attempts = 1
    for attempt in range(max_attempts):
        try:
            process = Popen(command_args, stdout=PIPE, stderr=STDOUT, encoding="utf-8")

            # Python Docs: this will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates
            # enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data.
            # I don't this was an issue for us yet, but something to keep in mind.
            process.wait(timeout)

            retval = process.poll()
            if retval != 0 and log:
                logger.warning("Return value: {:}".format(retval))

        except subprocess.TimeoutExpired as e:
            if log:
                logger.debug("Timeout expired on attempt {:d}. Retrying {:}".format(attempt+1, e))

            # TODO: fix this case where programs timeout.
            if log:
                logger.debug("Returning after user code timed out.")
            return process, -1, "Your program took too long to run (more than 10 seconds)."

        else:
            retval = process.poll()
            stdout_str = process.stdout.read()

            if len(stdout_str.strip()) > 0 and log:
                logger.debug("stdout+err:\n{:}".format(stdout_str.strip()))

            return process, retval, stdout_str

    else:
        if log:
            logger.debug("Max attempts ({:d}) tried.".format(max_attempts))


def _stdout_to_str(text_io_wrapper):
    line = text_io_wrapper.readline()
    total = ""

    while line:
        logger.debug(line)
        print(line, end="")
        line = text_io_wrapper.readline()
        total += line

    return total

