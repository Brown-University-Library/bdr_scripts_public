"""
Downloads MODS XML files for a list of BDR PIDs.
"""

import argparse
import logging
import os
import time
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from pathlib import Path

import httpx
from dotenv import load_dotenv

## the dotenv-directory is in the "stuff" directory.
DOTENV_PATH: Path = Path(__file__).resolve().parents[2] / 'dot_env_files' / 'save_mods_to_dir.env'

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


LOGLEVEL: str = os.getenv('SM__LOGLEVEL', 'INFO')
MODS_URL_PATTERN: str = get_env_var('SM__MODS_URL_PATTERN')
PROCESSES: int = int(os.getenv('SM__PROCESSES', '2'))
REQUEST_TIMEOUT: float = float(os.getenv('SM__REQUEST_TIMEOUT', '30'))


## setup console logging
LOG_LEVELS: dict[str, int] = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
}
logging.basicConfig(
    level=LOG_LEVELS.get(LOGLEVEL, logging.INFO),
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
)
log = logging.getLogger(__name__)


def config_parser() -> argparse.ArgumentParser:
    """
    Configures the argument parser.

    Called by: main()
    """
    desc = """Downloads MODS files, concurrently, to the specified directory, for given PIDs.
- Takes an output-directory filepath and a filepath to a list of BDR PIDs as arguments.
- More info: <https://github.com/Brown-University-Library/bdr_scripts_public/blob/main/save_mods_to_dir/README.md>.
"""
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--check_envars', required=False, action='store_true', help='optional; displays envars, and exits')
    parser.add_argument('--output_dir_path', required=False, help='required; full-path to the output_directory')
    parser.add_argument(
        '--pids_list_path', required=False, help='required; filepath to a file of BDR PIDs, one PID per line'
    )
    return parser


def display_envars() -> None:
    """
    Displays environment configuration.

    Called by: main()
    """
    print(
        f"""
Envars:

For this `save_mods.py` script...
- DOTENV_PATH, ``{DOTENV_PATH}``
- LOGLEVEL, ``{LOGLEVEL}``
- MODS_URL_PATTERN, ``{MODS_URL_PATTERN}``
- PROCESSES, ``{PROCESSES}``
- REQUEST_TIMEOUT, ``{REQUEST_TIMEOUT}``

(end)
"""
    )
    raise SystemExit(0)


def validate_path(arg_path: str) -> Path:
    """
    Validates that an argument path exists.

    Called by: main()
    """
    path = Path(arg_path).resolve()
    if not path.exists():
        raise SystemExit(f'path does not exist: {arg_path}')
    return path


def make_output_filepath(output_dir_path: Path, pid: str) -> Path:
    """
    Creates the output filepath for a PID's MODS XML file.

    Called by: download_mods()
    """
    pid_stem = pid.replace(':', '_')
    output_filepath = output_dir_path / f'{pid_stem}__MODS.xml'
    log.debug('output_filepath, ``%s``', output_filepath)
    return output_filepath


def grab_and_save_mods(url: str, output_filepath: Path, pid: str) -> bool:
    """
    Gets and saves one MODS XML file.

    Called by: download_mods()
    """
    saved = False
    log.debug('url, ``%s``', url)
    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(url)
        if response.status_code == httpx.codes.OK:
            output_filepath.write_bytes(response.content)
            saved = True
        else:
            log.warning('failed to retrieve the file for pid, ``%s``. HTTP status code: %s', pid, response.status_code)
    except httpx.HTTPError as err:
        log.warning('error getting MODS for pid, ``%s``: %s', pid, err)
    return saved


def check_well_formed_xml(output_filepath: Path, pid: str) -> bool:
    """
    Checks whether a saved MODS XML file is well-formed.

    Called by: download_mods()
    """
    validity = False
    try:
        ET.parse(output_filepath)
        validity = True
    except ET.ParseError:
        log.warning('MODS for pid, ``%s`` is not well-formed XML', pid)
    log.debug('validity, ``%s``', validity)
    return validity


def download_mods(pid: str, output_dir_path: Path, index: int) -> None:
    """
    Downloads one PID's MODS XML file to the specified directory.

    Called by: run_multiprocessing()
    """
    log.debug('processing pid, ``%s``', pid)
    url = MODS_URL_PATTERN.format(PID_VAR=pid)
    output_filepath = make_output_filepath(output_dir_path, pid)
    saved = grab_and_save_mods(url, output_filepath, pid)
    if saved:
        check_well_formed_xml(output_filepath, pid)
    if (index + 1) % 10 == 0:
        log.info('Processed %s items.', index + 1)


def read_pids(pids_list_path: Path) -> list[str]:
    """
    Reads BDR PIDs from a text file.

    Called by: run_multiprocessing()
    """
    pids = pids_list_path.read_text(encoding='utf-8').splitlines()
    pids = [pid.strip() for pid in pids if pid.strip()]
    log.info('pids to process, ``%s``', pids)
    return pids


def run_multiprocessing(output_dir_path: Path, pids_list_path: Path) -> None:
    """
    Runs the MODS downloads in parallel processes.

    Called by: main()
    """
    pids = read_pids(pids_list_path)
    args = [(pid, output_dir_path, index) for index, pid in enumerate(pids)]
    with Pool(processes=PROCESSES) as pool:
        pool.starmap(download_mods, args)


def main() -> None:
    """
    Parses CLI args and starts MODS downloads.

    Called by: command line
    """
    parser = config_parser()
    args = parser.parse_args()
    if args.check_envars:
        display_envars()
    if not args.output_dir_path or not args.pids_list_path:
        raise SystemExit('Both --output_dir_path and --pids_list_path are required.')
    output_dir_path = validate_path(args.output_dir_path)
    pids_list_path = validate_path(args.pids_list_path)
    start_time = time.monotonic()
    run_multiprocessing(output_dir_path, pids_list_path)
    elapsed_time = time.monotonic() - start_time
    log.info('total elapsed time, ``%.2f`` seconds', elapsed_time)


if __name__ == '__main__':
    main()
