import logging
import os
import subprocess
from subprocess import CalledProcessError

import docker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


def docker_init(client=None, image_name="lovelace-code-test"):
    """Build docker image for code test containers

    Syntax to build docker image (from inside Dockerfile dir):
    docker build -t <image_name> .

    Syntax to build docker image (from OUTSIDE Dockerfile dir):
    docker build -t <image_name> -f /path/to/Dockerfile /path/to/docker_dir
    """

    if not client:
        client = docker.from_env()

    docker_dir = os.path.dirname(SCRIPT_DIR)
    logger.info(
        'Building docker image "{}" for code test containers in {}'.format(image_name, docker_dir)
    )

    try:
        image, logs = client.images.build(
            path=docker_dir, dockerfile="code_runner.Dockerfile", tag="lovelace-code-test"
        )
    except (docker.errors.BuildError, docker.errors.APIError):
        logger.error(
            "Failed to build docker image! Please check that docker is installed and that "
            "the engine has access to run docker commands."
        )
        raise


def create_docker_container(client=None, name=None, image_name="lovelace-code-test", remove=False):
    """Create a docker container

    Syntax to create a docker container (as daemon):
    docker run -d --name <container_name> <image_name>

    Note: container name must be unique.
    """

    if not client:
        client = docker.from_env()

    logger.info('Creating docker container "{}" from image "{}"'.format(name, image_name))

    # Max 40% cpu usage
    cpu_period = 100000
    cpu_quota = 40000

    # Max 512 MiB memory limit
    mem_limit = "512m"

    try:
        container = client.containers.run(image_name, detach=True, name=name, remove=remove,
                                          cpu_period=cpu_period, cpu_quota=cpu_quota, mem_limit=mem_limit)
    except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError):
        logger.error(
            "Failed to start docker container! Please check that docker is installed and that "
            "the engine has access to run docker commands."
        )
        raise

    return container.id, container.name


def remove_docker_container(container_id):

    # TODO: this is called TWICE when gunicorn shuts down. Maybe because of the way the reloader
    # works?

    logger.info("Clean up:  deleting container {}".format(container_id))

    client = docker.from_env()

    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        logger.info("Container {} already deleted!".format(container_id))
        return
    container.stop()
    container.remove()
    logger.info("Container deleted successfully")


def docker_file_push(container_id, src_path, tgt_path, container_user="root", chown=True):
    """Copy a file into a docker container"""

    cmd = ["docker", "cp", src_path, "{}:{}".format(container_id, tgt_path)]
    copy_msg = "{}: {} -> {}".format(container_id, src_path, tgt_path)
    logger.debug("Copying file into docker container: " + copy_msg)

    try:
        ret = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, encoding="utf8")
    except CalledProcessError as e:
        logger.error("Failed to copy file into container " + copy_msg)
        logger.error("Process return code: {}; stdout: {}".format(e.returncode, e.stdout))
        raise

    # TODO chown?

    return ret.stdout


def docker_file_pull(container_id, src_path, tgt_path):
    """Copy a file out of a docker container"""

    cmd = ["docker", "cp", "{}:{}".format(container_id, src_path), tgt_path]
    copy_msg = "{}: {} -> {}".format(container_id, src_path, tgt_path)
    logger.debug("Copying file out of docker container: " + copy_msg)

    try:
        ret = subprocess.run(cmd, check=True, stderr=subprocess.STDOUT, encoding="utf8")
    except CalledProcessError as e:
        logger.error("Failed to copy file out of container " + copy_msg)
        logger.error("Process return code: {}; stdout: {}".format(e.returncode, e.stdout))
        raise

    return ret.stdout


def docker_execute(container_id, cmd, timeout=30, env=None, client=None):
    """Execute a command in a docker container"""

    if not client:
        client = docker.from_env()

    try:
        container = client.containers.get(container_id)
    except docker.errors.NotFound:
        logger.error(f"Container {container_id} could not be found.")
        raise

    timeout_cmd = ["timeout", f"{timeout}"]
    full_cmd = timeout_cmd + cmd

    logger.debug(f"Running command {full_cmd} in container {container_id}.")

    try:
        exit_code, std_out = container.exec_run(full_cmd, environment=env, workdir=None)
    except docker.errors.APIError:
        logger.error(
            f'Failed to run cmd {full_cmd} in container {container_id}.'
            f'Exit code: {exit_code}; Stdout: {std_out.decode("utf8")}'
        )
        raise

    return exit_code, std_out.decode("utf8")
