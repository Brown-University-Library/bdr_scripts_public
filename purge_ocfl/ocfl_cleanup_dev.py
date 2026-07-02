import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

DOTENV_PATH: Path = Path(__file__).resolve().parent / 'dot_env_files' / 'ocfl_cleanup_dev.env'

# load variables from script-specific dotenv file
load_dotenv(DOTENV_PATH)
OCFL_DIR = os.getenv('OCFL_DIR')
ROCFL_CMD = os.getenv('ROCFL_CMD')
LOG_FILE = os.getenv('LOG_FILE')
PIDS_FILE = os.getenv('PIDS_FILE')
DRY_RUN = os.getenv('DRY_RUN')


# set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)


def setup_stuff():
    # Prompt user to continue as this script will delete OCFL directories
    reply = input('This script will PERMANENTLY delete OCFL directories! Do you want to continue? (y/n) ')
    if not reply.lower().startswith('y'):
        log.info('Exiting...')
        exit(1)

    # Check if pids_to_delete.txt file exists
    if not os.path.exists(PIDS_FILE):
        log.info(f'{PIDS_FILE} does not exist')
        exit(1)

    # Change to OCFL directory
    try:
        os.chdir(OCFL_DIR)
        log.info(f'Changed to {OCFL_DIR}')
    except Exception:
        log.exception(f'Failed to change directory to {OCFL_DIR}')
        exit(1)


def read_pids():
    # Read pids from file
    with open(PIDS_FILE, 'r', encoding='ascii') as file:
        pids_to_delete = file.read().splitlines()
    log.info(f'Read {len(pids_to_delete)} pids from {PIDS_FILE}')
    return pids_to_delete


if __name__ == '__main__':
    log.info('Starting...')

    setup_stuff()
    pids_to_delete = read_pids()
    assert len(pids_to_delete) > 0, 'No pids found in file'

    # Loop through pids and delete OCFL directories
    for pid in pids_to_delete:
        log.info(f'Processing {pid}')

        # if OCFL object exists, purge it
        result = subprocess.run([ROCFL_CMD, 'ls', pid], stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            # if DRY_RUN is set to True, simply log the command that would be run
            if DRY_RUN.lower() == 'true':
                log.info(f'DRY RUN: {ROCFL_CMD} purge {pid} --force')
            elif DRY_RUN.lower() == 'false':
                # Note: if you want to get prompted for confirmation, remove the --force flag
                subprocess.run([ROCFL_CMD, 'purge', pid, '--force'])
                log.info(f'Purged {pid} from {OCFL_DIR}')
            else:
                log.info("DRY_RUN must be set to either 'true' or 'false'")
                exit(1)
        else:
            log.info(f'No OCFL object found for {pid} in {OCFL_DIR}')

    log.info('...Done')
