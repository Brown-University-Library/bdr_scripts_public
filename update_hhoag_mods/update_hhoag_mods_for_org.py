"""
Updates Hall-Hoag organization MODS and item MODS files in the BDR.
"""

import argparse
import collections
import json
import logging
import os
import subprocess
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

## the dotenv-directory is in the "stuff" directory.
DOTENV_PATH: Path = Path(__file__).resolve().parents[2] / 'dot_env_files' / 'update_hhoag_mods.env'

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


BDR_API_ROOT: str = get_env_var('UHHM__BDR_API_URL_ROOT').rstrip('/')
LOGLEVEL: str = os.getenv('UHHM__LOGLEVEL', 'DEBUG')
BINARY_PATH: str = get_env_var('UHHM__UPDATE_MODS_BINARY_PATH')
LOG_PATH: Path = Path(os.getenv('UHHM__LOG_PATH', '../logs/update_hhoag_mods.log')).resolve()
REQUEST_TIMEOUT: float = float(os.getenv('UHHM__REQUEST_TIMEOUT', '30'))

## for the `update_mods` python-binary
BINARY_API_AGENT: str = get_env_var('UM__API_AGENT')
BINARY_API_IDENTITY: str = get_env_var('UM__API_IDENTITY')
BINARY_API_ROOT_URL: str = get_env_var('UM__API_ROOT_URL')
BINARY_LOGLEVEL: str = os.getenv('UM__LOGLEVEL', 'INFO')
BINARY_MESSAGE: str = get_env_var('UM__MESSAGE')


## setup logging
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
LOG_FORMAT = '[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s'
DATE_FORMAT = '%d/%b/%Y %H:%M:%S'
LOG_LEVELS: dict[str, int] = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
}
logging.basicConfig(
    level=LOG_LEVELS.get(LOGLEVEL, logging.DEBUG),
    format=LOG_FORMAT,
    filename=LOG_PATH,
    datefmt=DATE_FORMAT,
)
log = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
log.addHandler(console_handler)
logging.getLogger('fontTools').setLevel(logging.WARNING)


def config_parser() -> argparse.ArgumentParser:
    """
    Configures parser.

    Called by: main()
    """
    parser = argparse.ArgumentParser(description='Updates Hall-Hoag MODS files for specified organizations.')
    parser.add_argument('--org_list', required=True, help='takes orgs to process; example "HH123456" or "HH123456,HH654321"')
    parser.add_argument(
        '--mods_dir', required=True, help='takes path to directory containing pre-made org-mods and item-mods files'
    )
    parser.add_argument('--tracker_dir', required=True, help='takes path to directory containing the tracker files')
    parser.add_argument('--check_envars', required=False, action='store_true', help='checks envars and exits')
    return parser


def validate_arg_paths(mods_directory_path: Path, tracker_directory_path: Path) -> None:
    """
    Validates argument paths.

    Called by: main()
    """
    if not mods_directory_path.exists():
        raise SystemExit(f'Error: The path {mods_directory_path} does not exist.')
    if not tracker_directory_path.is_dir():
        raise SystemExit(f'Error: The path {tracker_directory_path} is not a directory.')


def display_envars() -> None:
    """
    Displays environment configuration.

    Called by: main()
    """
    print(
        f"""
Envars:

For this `update_hhoag_mods_for_org.py` script...
- DOTENV_PATH, ``{DOTENV_PATH}``
- BDR_API_ROOT, ``{BDR_API_ROOT}``
- LOGLEVEL, ``{LOGLEVEL}``
- LOG_PATH, ``{LOG_PATH}``
- REQUEST_TIMEOUT, ``{REQUEST_TIMEOUT}``

For the `update_mods_python_binary` file...
- BINARY_PATH, ``{BINARY_PATH}``
- BINARY_API_AGENT, ``{BINARY_API_AGENT}``
- BINARY_API_IDENTITY, ``{BINARY_API_IDENTITY}``
- BINARY_API_ROOT_URL, ``{BINARY_API_ROOT_URL}``
- BINARY_LOGLEVEL, ``{BINARY_LOGLEVEL}``
- BINARY_MESSAGE, ``{BINARY_MESSAGE}``

(end)
"""
    )
    raise SystemExit(0)


def get_org_tracker_filepath(org: str, tracker_directory_path: Path) -> Path:
    """
    Gets the org's tracker file path.

    Called by: manage_org_mods_update()
    """
    part_a, part_b = org[:4], org[4:8]
    org_tracker_filepath = tracker_directory_path / part_a / part_b / f'{org}__whole_org_updated.json'
    log.debug('org_tracker_filepath, ``%s``', org_tracker_filepath)
    return org_tracker_filepath


def check_tracker(tracker_filepath: Path) -> bool:
    """
    Checks whether an org or item tracker file already exists.

    Called by: manage_org_mods_update()
    """
    return_val = tracker_filepath.exists()
    log.debug('return_val `%s`', return_val)
    return return_val


def parse_id(mods_file: Path) -> str:
    """
    Returns a Hall-Hoag ID from a MODS filepath.

    Called by: get_filepath_data()
    """
    filename_a = mods_file.stem
    filename_b = filename_a.split('.')[0]
    return filename_b


def get_filepath_data(org: str, mods_directory_path: Path) -> collections.OrderedDict[str, dict[str, Path]]:
    """
    Creates org-data and populates it with filepath info.

    Called by: manage_org_mods_update()
    """
    org_data: dict[str, dict[str, Path]] = {}
    mods_paths = list(mods_directory_path.rglob('*mods.xml'))
    for mods_filepath in mods_paths:
        if org in mods_filepath.name:
            hh_id = parse_id(mods_filepath)
            org_data[hh_id] = {'path': mods_filepath}
    sorted_org_data = collections.OrderedDict(sorted(org_data.items()))
    log.debug('org_data, partial, ``%s...``', str(sorted_org_data)[:1000])
    return sorted_org_data


def get_org_data_via_api(org: str) -> list[dict[str, object]]:
    """
    Gets org data from the BDR public API.

    Called by: manage_org_mods_update()
    """
    api_data: list[dict[str, object]] = []
    start = 0
    rows = 500
    params = {
        'q': f'mods_id_local_ssim:*{org}*',
        'fl': 'mods_id_local_ssim,primary_title,pid',
        'rows': rows,
    }
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        while True:
            params['start'] = start
            log.debug('calling %s/search/ with params %s', BDR_API_ROOT, params)
            response = client.get(f'{BDR_API_ROOT}/search/', params=params)
            response.raise_for_status()
            response_data = response.json()
            docs = response_data['response']['docs']
            api_data.extend(docs)
            if len(docs) < rows:
                break
            start += rows
    log.debug('api_data, partial, ``%s...``', str(api_data)[:1000])
    return api_data


def merge_api_data_into_org_data(
    org_data: collections.OrderedDict[str, dict[str, object]],
    api_data: list[dict[str, object]],
) -> collections.OrderedDict[str, dict[str, object]]:
    """
    Merges BDR API PID data into org data.

    Called by: manage_org_mods_update()
    """
    for api_item in api_data:
        hh_ids = api_item.get('mods_id_local_ssim', [])
        if not hh_ids:
            continue
        hh_id = str(hh_ids[0])
        if hh_id in org_data:
            org_data[hh_id]['pid'] = api_item['pid']
    log.debug('updated org_data, partial, ``%s...``', str(org_data)[:1000])
    ids_missing_pids = [hh_id for hh_id, item_dict in org_data.items() if 'pid' not in item_dict]
    if ids_missing_pids:
        log.warning('WARNING: these items are missing pids: ``%s``', ids_missing_pids)
    return org_data


def get_item_tracker_filepath(hh_id: str, tracker_directory_path: Path) -> Path:
    """
    Gets the item's tracker file path.

    Called by: manage_item_loop()
    """
    part_a, part_b = hh_id[:4], hh_id[4:8]
    item_tracker_filepath = tracker_directory_path / part_a / part_b / f'{hh_id}__item_updated.json'
    log.debug('item_tracker_filepath, ``%s``', item_tracker_filepath)
    return item_tracker_filepath


def call_api(path: Path, pid: str) -> str:
    """
    Calls the update-MODS binary for one item.

    Called by: manage_item_loop()
    """
    log.debug('path, ``%s``; pid, ``%s``', path, pid)
    env_copy = os.environ.copy()
    cmd = [BINARY_PATH, '--mods_filepath', str(path), '--bdr_pid', pid]
    log.debug('cmd, ``%s``', cmd)
    result = subprocess.run(cmd, env=env_copy, capture_output=True, text=True, check=False)
    log.debug('result, ``%s``', result)
    return_data = ''
    if result.stderr:
        log.warning('WARNING, stderr returned, ``%s``', result.stderr)
        return_data = result.stderr
    return return_data


def update_item_tracker(item_tracker_filepath: Path, err: str) -> None:
    """
    Updates the item's tracker file.

    Called by: manage_item_loop()
    """
    item_tracker_filepath.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if not err:
        msg = json.dumps({'timestamp': timestamp, 'message': 'all_good'}, sort_keys=True, indent=2)
        item_tracker_filepath.write_text(msg, encoding='utf-8')
    else:
        new_filename = item_tracker_filepath.name.replace('__item_updated.json', '__item_problem.json')
        new_filepath = item_tracker_filepath.parent / new_filename
        err_msg = json.dumps({'timestamp': timestamp, 'err': err}, sort_keys=True, indent=2)
        new_filepath.write_text(err_msg, encoding='utf-8')


def update_org_tracker(org_tracker_filepath: Path) -> None:
    """
    Updates the org's tracker file.

    Called by: manage_org_mods_update()
    """
    org_tracker_filepath.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    msg = json.dumps({'timestamp': timestamp, 'message': 'org_processed'}, sort_keys=True, indent=2)
    org_tracker_filepath.write_text(msg, encoding='utf-8')


def manage_item_loop(
    org_data: collections.OrderedDict[str, dict[str, object]],
    tracker_directory_path: Path,
) -> None:
    """
    Updates item MODS and item tracker files for one org.

    Called by: manage_org_mods_update()
    """
    for hh_id, item_dict in org_data.items():
        item_tracker_filepath = get_item_tracker_filepath(hh_id, tracker_directory_path)
        if check_tracker(item_tracker_filepath):
            continue
        if 'pid' not in item_dict:
            err_msg = f'WARNING: pid not found for item ``{hh_id}``'
            log.warning('\n%s\n', err_msg)
            update_item_tracker(item_tracker_filepath, err_msg)
            continue
        mods_path = item_dict['path']
        pid = str(item_dict['pid'])
        log.info('\nprocessing item ``%s-%s``\n', hh_id, pid)
        err = call_api(Path(str(mods_path)), pid)
        update_item_tracker(item_tracker_filepath, err)


def manage_org_mods_update(orgs_list: list[str], mods_directory_path: Path, tracker_directory_path: Path) -> None:
    """
    Updates MODS files and trackers for the requested orgs.

    Called by: main()
    """
    for org in orgs_list:
        log.info('\n\nprocessing org, ``%s``', org)
        org_tracker_filepath = get_org_tracker_filepath(org, tracker_directory_path)
        if check_tracker(org_tracker_filepath):
            continue
        org_data = get_filepath_data(org, mods_directory_path)
        api_data = get_org_data_via_api(org)
        merged_org_data = merge_api_data_into_org_data(org_data, api_data)
        manage_item_loop(merged_org_data, tracker_directory_path)
        update_org_tracker(org_tracker_filepath)
        log.info('finished processing org, ``%s``', org)


def main() -> None:
    """
    Parses CLI args and updates Hall-Hoag MODS files.

    Called by: command line
    """
    start_time = time.monotonic()
    parser = config_parser()
    args = parser.parse_args()
    orgs_list = [org.strip() for org in args.org_list.split(',') if org.strip()]
    mods_directory_path = Path(args.mods_dir).resolve()
    tracker_directory_path = Path(args.tracker_dir).resolve()
    validate_arg_paths(mods_directory_path, tracker_directory_path)
    if args.check_envars:
        display_envars()
    manage_org_mods_update(orgs_list, mods_directory_path, tracker_directory_path)
    elapsed_time = time.monotonic() - start_time
    log.info('total elapsed time for all orgs, ``%.2f`` seconds', elapsed_time)


if __name__ == '__main__':
    main()
