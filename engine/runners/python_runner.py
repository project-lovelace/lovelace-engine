import logging
import pickle
import shutil

import engine.util as util
from .abstract_runner import AbstractRunner
from ..simple_lxd import simple_lxd as lxd

logger = logging.getLogger(__name__)


class PythonRunner(AbstractRunner):
    def run(self, code_filename, input_tuple):
        logger.debug("Running {:s} with input {:s}".format(code_filename, input_tuple))

        run_id = code_filename.split('.')[0]
        input_pickle = '{}.input.pickle'.format(run_id)
        with open(input_pickle, mode='wb') as f:
            logger.debug("Pickling input tuple in {:s}...".format(input_pickle))
            pickle.dump(input_tuple, file=f)

        runner_file = "{}.run.py".format(run_id)
        shutil.copy("run_it.py", runner_file)

        container_name = 'lovelace-{}'.format(run_id)
        lxd.launch(
            "images:ubuntu/xenial/i386",
            name=container_name,
            profile="lovelace"
        )

        for file_name in [code_filename, runner_file, input_pickle]:
            source_path = file_name
            target_path = "/tmp/{}".format(file_name)
            lxd.file_push(container_name, source_path, target_path)

        runner_path = "/tmp/{}".format(runner_file)
        command = ['python3', runner_path]
        lxd.execute(container_name, command)

        p_info = {
            'returnCode': 0,
            'utime': 0,
            'stime': 0,
            'maxrss': 0,
        }

        output_pickle = '{}.output.pickle'.format(run_id)
        source_path = '/tmp/{}'.format(output_pickle)
        target_path = output_pickle

        lxd.file_pull(container_name, source_path, target_path)

        with open(output_pickle, mode='rb') as f:
            user_output = pickle.load(f)

        logger.debug("Finished running user code. Return code %d.", p_info['returnCode'])
        logger.debug("utime: %f, stime: %f", p_info['utime'], p_info['stime'])
        logger.debug("maxrss: %d kB", p_info['maxrss'])  # resource

        util.delete_file(input_pickle)
        util.delete_file(output_pickle)
        util.delete_file(runner_file)

        return user_output, p_info
