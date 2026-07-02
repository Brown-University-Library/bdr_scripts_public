# save MODS to directory

## Purpose

This utility downloads MODS XML files for a reviewed list of BDR PIDs and writes them to a local output directory. It is intended for batch preparation work where the caller already has a PID list and needs local MODS files for follow-up review or processing.

## What this does

`save_mods.py` reads configuration from `../../dot_env_files/save_mods_to_dir.env`, including the MODS URL pattern, log level, request timeout, and process count. It accepts an output directory and a PID-list file, downloads each PID's MODS XML concurrently, writes each file as `<pid>__MODS.xml` with colons converted to underscores, and checks that saved files are well-formed XML.

Downloaded MODS files must be written outside the `bdr_scripts_public` git repository.

## Usage

From the `save_mods_to_dir` directory:

1. Create the dotenv and output directories if they do not already exist:

```shell
mkdir -p ../../dot_env_files
mkdir -p ../../output_files/save_mods_to_dir
```

2. Copy `sample.env` to the script-specific dotenv path:

```shell
cp ./sample.env ../../dot_env_files/save_mods_to_dir.env
```

3. Edit `../../dot_env_files/save_mods_to_dir.env` so these values match the target environment:
    - `SM__MODS_URL_PATTERN`: URL pattern used to download MODS; include `{PID_VAR}` where the BDR PID should be inserted.
    - `SM__LOGLEVEL`: optional log level, usually `INFO` or `DEBUG`.
    - `SM__PROCESSES`: optional number of parallel worker processes.
    - `SM__REQUEST_TIMEOUT`: optional HTTP timeout in seconds.
4. Run the script with `uv`:

```shell
uv run ./save_mods.py --output_dir_path "../../output_files/save_mods_to_dir" --pids_list_path "/path/to/bdr_pids.txt"
```

To confirm configuration without downloading files:

```shell
uv run ./save_mods.py --check_envars
```

See `sample.env` for the expected configuration values.
