import logging
import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

## the dotenv-directory is in the "stuff" directory.
DOTENV_PATH: Path = Path(__file__).resolve().parents[2] / 'dot_env_files' / 'ocfl_cleanup_dev.env'
REPO_ROOT: Path = Path(__file__).resolve().parents[1]
STUFF_ROOT: Path = Path(__file__).resolve().parents[2]

## load variables from script-specific dotenv file
load_dotenv(DOTENV_PATH)


def get_env_var(env_var_name: str) -> str:
    """
    Gets a required environment variable.

    Called by: module initialization
    """
    env_var_value = os.getenv(env_var_name)
    if not env_var_value:
        raise SystemExit(f'{env_var_name} must be set in {DOTENV_PATH}')
    return env_var_value


def resolve_external_path(path_value: str, path_description: str) -> Path:
    """
    Resolves an output path and rejects paths inside the git repository.

    Called by: module initialization
    """
    raw_path = Path(path_value)
    path = raw_path if raw_path.is_absolute() else STUFF_ROOT / raw_path
    resolved_path = path.resolve()
    if resolved_path.is_relative_to(REPO_ROOT):
        raise SystemExit(f'{path_description} must be outside the git repository: {resolved_path}')
    return resolved_path


OCFL_DIR: Path = Path(get_env_var('OCFL_DIR'))
ROCFL_CMD: str = get_env_var('ROCFL_CMD')
LOG_FILE: Path = resolve_external_path(get_env_var('LOG_FILE'), 'LOG_FILE')
PIDS_FILE: Path = Path(get_env_var('PIDS_FILE'))
DRY_RUN: str = get_env_var('DRY_RUN')


## set up logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)


def setup_stuff() -> None:
    """
    Confirms destructive intent and prepares the OCFL working directory.

    Called by: main()
    """
    ## Prompt user to continue as this script will delete OCFL directories
    reply = input('This script will PERMANENTLY delete OCFL directories! Do you want to continue? (y/n) ')
    if not reply.lower().startswith('y'):
        log.info('Exiting...')
        raise SystemExit(1)

    ## Check if pids_to_delete.txt file exists
    if not PIDS_FILE.exists():
        log.info('%s does not exist', PIDS_FILE)
        raise SystemExit(1)

    ## Change to OCFL directory
    try:
        os.chdir(OCFL_DIR)
        log.info('Changed to %s', OCFL_DIR)
    except OSError:
        log.exception('Failed to change directory to %s', OCFL_DIR)
        raise SystemExit(1) from None


def read_pids() -> list[str]:
    """
    Reads the BDR PIDs selected for OCFL cleanup.

    Called by: main()
    """
    ## Read pids from file
    with PIDS_FILE.open(encoding='ascii') as file:
        pids_to_delete = file.read().splitlines()
    log.info('Read %s pids from %s', len(pids_to_delete), PIDS_FILE)
    return pids_to_delete


def purge_pid(pid: str) -> None:
    """
    Purges one PID from OCFL storage when it exists and dry-run mode is disabled.

    Called by: main()
    """
    log.info('Processing %s', pid)

    ## if OCFL object exists, purge it
    result = subprocess.run([ROCFL_CMD, 'ls', pid], stdout=subprocess.DEVNULL, check=False)
    if result.returncode == 0:
        ## if DRY_RUN is set to True, simply log the command that would be run
        if DRY_RUN.lower() == 'true':
            log.info('DRY RUN: %s purge %s --force', ROCFL_CMD, pid)
        elif DRY_RUN.lower() == 'false':
            ## Note: if you want to get prompted for confirmation, remove the --force flag
            subprocess.run([ROCFL_CMD, 'purge', pid, '--force'], check=False)
            log.info('Purged %s from %s', pid, OCFL_DIR)
        else:
            log.info("DRY_RUN must be set to either 'true' or 'false'")
            raise SystemExit(1)
    else:
        log.info('No OCFL object found for %s in %s', pid, OCFL_DIR)


def main() -> None:
    """
    Orchestrates OCFL cleanup for the configured PID list.

    Called by: command line
    """
    log.info('Starting...')

    setup_stuff()
    pids_to_delete = read_pids()
    if not pids_to_delete:
        raise SystemExit('No pids found in file')

    ## Loop through pids and delete OCFL directories
    for pid in pids_to_delete:
        purge_pid(pid)

    log.info('...Done')


if __name__ == '__main__':
    main()
