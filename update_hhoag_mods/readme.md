# update Hall-Hoag MODS

## Purpose

This utility updates BDR MODS records for selected Hall-Hoag organizations from pre-produced local MODS files. It is intended for controlled batch update work where MODS files have already been generated and reviewed.

## What this does

`update_hhoag_mods_for_org.py` reads configuration from `../../dot_env_files/update_hhoag_mods.env`, including the BDR public API root, update-MODS binary path, API credentials used by that binary, log settings, and request timeout. For each requested Hall-Hoag organization, the script finds matching local `*mods.xml` files, queries the BDR public API to map Hall-Hoag IDs to BDR PIDs, skips items that already have tracker files, calls the configured update-MODS binary for each unprocessed item, writes item tracker files, and writes an org tracker file after the org has been processed.

## Usage

From the `update_hhoag_mods` directory:

1. Create the dotenv directory if it does not already exist:

```shell
mkdir -p ../../dot_env_files
```

2. Copy `sample.env` to the script-specific dotenv path:

```shell
cp ./sample.env ../../dot_env_files/update_hhoag_mods.env
```

3. Edit `../../dot_env_files/update_hhoag_mods.env` so these values match the target update environment:
    - `UHHM__BDR_API_URL_ROOT`: BDR public API root URL, without the trailing `/search/`.
    - `UHHM__UPDATE_MODS_BINARY_PATH`: full path to the update-MODS executable.
    - `UHHM__LOG_PATH`: optional log-file path.
    - `UHHM__LOGLEVEL`: optional file log level, usually `INFO` or `DEBUG`.
    - `UHHM__REQUEST_TIMEOUT`: optional BDR public API timeout in seconds.
    - `UM__API_AGENT`, `UM__API_IDENTITY`, `UM__API_ROOT_URL`, `UM__LOGLEVEL`, and `UM__MESSAGE`: values passed through the environment to the update-MODS binary.
4. Run the script with `uv`:

```shell
uv run ./update_hhoag_mods_for_org.py --org_list "HH123456,HH654321" --mods_dir "/path/to/mods_dir" --tracker_dir "/path/to/tracker_dir"
```

To confirm configuration without updating MODS:

```shell
uv run ./update_hhoag_mods_for_org.py --org_list "HH123456" --mods_dir "/path/to/mods_dir" --tracker_dir "/path/to/tracker_dir" --check_envars
```

See `sample.env` for the expected configuration values.
