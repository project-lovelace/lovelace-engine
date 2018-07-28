import os
import logging, logging.config
import importlib
import psutil

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger(__name__)

submission_filename = 'user_submitted_code.py'
submission_module = 'user_submitted_code'

problem_name = 'i04_dna_transcription'
problem_module = 'i04_dna_transcription'  # Could be 'problems.i04_dna_transcription'
function_name = 'dna_complement'

if __name__ == '__main__':
    logger.info('Importing problem module: {:s}'.format(problem_module))
    problem = importlib.import_module(problem_module)

    logger.info("Generating test cases...")
    test_case_type_enum = problem.TEST_CASE_TYPE_ENUM
    test_cases = []
    for i, test_type in enumerate(test_case_type_enum):
        for j in range(test_type.multiplicity):
            logger.debug("Generating test case {}: {} ({}/{})..."
                .format(len(test_cases)+1, str(test_type), j+1, test_type.multiplicity))
            test_cases.append(problem.generate_input(test_type))

    num_passes = 0
    num_cases = len(test_cases)
    test_case_details = []  # List of dicts each containing the details of a particular test case.

    logger.info('Importing submission: {:s}'.format(submission_module))
    submission = importlib.import_module(submission_module)

    for i, tc in enumerate(test_cases):

        input_args = tc.input_args()
        user_output = submission.dna_complement(input_args)

        logger.info("Test case %d/%d (%s).", i+1, num_cases, tc.test_type.test_name)
        logger.debug("Input arguments:")
        logger.debug("%s", input_args)
        logger.debug("User output:")
        logger.debug("%s", user_output)