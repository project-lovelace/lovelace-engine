import os
from subprocess import Popen, PIPE, STDOUT


class LXDError(Exception):
    pass


def launch(image, name, ephemeral=False, profile=None, config=None,
           instance_type=None):
    """Create and start containers from images.
    Syntax: lxc launch [<remote>:]<image> [<remote>:][<name>] [--ephemeral|-e]
        [--profile|-p <profile>...] [--config|-c <key=value>...]
        [--type|-t <instance type>]
    :param image:
    :param name:
    :param ephemeral:
    :param profile:
    :param config:
    :param instance_type:
    :return: str
    """
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
    """Pull files from containers.
    Syntax: lxc file pull [<remote>:]<container>/<path>
        [[<remote>:]<container>/<path>...] <target path>
    :return:
    """
    command = ["lxc", "file", "pull"]
    from_path = os.path.join(container, source_path)
    command.append(container + from_path)
    command.append(target_path)
    return _run(command)


def file_push(container, source_path, target_path,
              uid=None, gid=None, mode=None):
    """Push files into containers.
    Syntax: lxc file push [--uid=UID] [--gid=GID] [--mode=MODE] <source path>
        [<source path>...] [<remote>:]<container>/<path>
    :return: str
    """
    command = ["lxc", "file", "push", "--force-local", "--verbose"]
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
    push_proc = _run(command)
    _stdout_to_str(push_proc.stdout)

    # TODO clean up this function, add max iterations
    check_if_pushed_cmd = ["test", "-f", target_path]
    exit_code = 1
    while exit_code == 1:
        push_proc = _run(command)
        exec_proc = execute(container, check_if_pushed_cmd)
        exit_code = exec_proc.poll()
        _stdout_to_str(exec_proc.stdout)

    return push_proc


def stop(container):
    """Stop running containers.
    Syntax: lxc stop [<remote>:]<container> [[<remote>:]<container>...]
    :return: str
    """
    command = ["lxc", "stop"]
    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)
    return _run(command)


def delete(container):
    """Delete containers and snapshots.
    Syntax: lxc delete [<remote>:]<container>[/<snapshot>]
        [[<remote>:]<container>[/<snapshot>]...]
    :return: str
    """
    command = ["lxc", "delete"]
    if type(container) is str:
        command.append(container)
    elif type(container) is list:
        for c in container:
            command.append(c)
    return _run(command)


def execute(container, command_line, mode="non-interactive", env=None):
    """
    Execute commands in containers.
    Syntax: lxc exec [<remote>:]<container>
        [--mode=auto|interactive|non-interactive] [--env KEY=VALUE...]
        [--] <command line>
    :param container:
    :param command_line:
    :param mode:
    :param env:
    :return:
    """
    command = ["lxc", "exec", container, "--mode={}".format(mode)]
    if env:
        command.append("--env")
        command.append(env)
    command.append("--")
    command.extend(command_line)
    return _run(command)


def profile_create(name, remote=None):
    """
    Create a new profile.
    Syntax: lxc profile create [<remote>:]<profile>
    :param remote:
    :param name:
    :return:
    """
    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "create", profile]
    return _run(command)


def profile_copy(src_name, dst_name, src_remote=None, dst_remote=None):
    """
    Copy the profile.
    Syntax: lxc profile copy [<remote>:]<profile> [<remote>:]<profile>
    :param src_name:
    :param dst_name:
    :param src_remote:
    :param dst_remote:
    :return:
    """
    src = "{}:{}".format(src_remote, src_name) if src_remote else src_name
    dst = "{}:{}".format(dst_remote, dst_name) if dst_remote else dst_name
    command = ["lxc", "profile", "copy", src, dst]
    return _run(command)


def profile_set(name, key, value, remote=None):
    """
    Set profile configuration.
    Syntax: lxc profile set [<remote>:]<profile> <key> <value>
    :param name:
    :param key:
    :param value:
    :param remote:
    :return:
    """
    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "set", profile, key, value]
    return _run(command)


def profile_delete(name, remote=None):
    """
    Delete a profile.
    Syntax: lxc profile delete [<remote>:]<profile>
    :param name:
    :param remote:
    :return:
    """
    profile = "{}:{}".format(remote, name) if remote else name
    command = ["lxc", "profile", "delete", profile]
    return _run(command)


def _run(command_args, timeout=100):
    process = Popen(command_args, stdout=PIPE, stderr=STDOUT, encoding="utf-8")
    process.wait(timeout)
    retval = process.poll()
    print("Return value {} from command {}".format(retval, " ".join(command_args)))
    for line in process.stdout:
        print('\t{}'.format(line), end='')
    # if retval != 0:
    #     raise LXDError
    return process


def _stdout_to_str(text_io_wrapper):
    line = text_io_wrapper.readline()
    total = ""
    while line:
        print(line, end="")
        line = text_io_wrapper.readline()
        total += line
    return total


if __name__ == '__main__':
    proc = launch("images:ubuntu/xenial/i386", "my-py-cont")
    _stdout_to_str(proc.stdout)
    proc = file_push("my-py-cont", "_hello.py", "/tmp/hello.py")
    _stdout_to_str(proc.stdout)
    proc = execute("my-py-cont", ["python3", "/tmp/hello.py"])
    _stdout_to_str(proc.stdout)
    proc = stop("my-py-cont")
    _stdout_to_str(proc.stdout)
    proc = delete("my-py-cont")
    _stdout_to_str(proc.stdout)
