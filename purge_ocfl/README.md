# ocfl cleanup script

## Purpose

This development utility removes known test or cleanup objects from an OCFL storage root by BDR PID. It is intended for controlled cleanup work where the PID list has already been reviewed and the caller explicitly wants matching OCFL objects purged with `rocfl`.

## What this does

`ocfl_cleanup_dev.py` deletes OCFL objects for a supplied list of BDR PIDs.

The script reads configuration from `../../dot_env_files/ocfl_cleanup_dev.env`, including the OCFL directory, the `rocfl` command path, a log-file path, a PID-list file, and `DRY_RUN`. It prompts before doing any work, changes into the configured OCFL directory, then checks each PID with `rocfl ls`.

Log files must be written outside the `bdr_scripts_public` git repository. Relative `LOG_FILE` values are resolved from the outer `bdr_PUBLIC_scripts_project_stuff` directory.

When `DRY_RUN` is set to `true`, the script logs the purge command that would run. When `DRY_RUN` is set to `false`, it runs `rocfl purge <pid> --force` for each PID found in the OCFL storage.

## Usage

From the `purge_ocfl` directory:

1. Create the dotenv and log directories if they do not already exist:

```shell
mkdir -p ../../dot_env_files
mkdir -p ../../log_files
```

2. Copy `sample.env` to the script-specific dotenv path:

```shell
cp ./sample.env ../../dot_env_files/ocfl_cleanup_dev.env
```

3. Edit `../../dot_env_files/ocfl_cleanup_dev.env` so these values point to the cleanup target:
    - `OCFL_DIR`: OCFL storage directory to inspect and purge from.
    - `ROCFL_CMD`: path to the `rocfl` executable.
    - `LOG_FILE`: file where cleanup activity should be logged; relative paths resolve from the outer directory, so `log_files/ocfl_cleanup_dev.log` becomes `../../log_files/ocfl_cleanup_dev.log`.
    - `PIDS_FILE`: text file containing one BDR PID per line.
    - `DRY_RUN`: set to `true` to log intended purge commands, or `false` to permanently purge matching OCFL objects.
4. Start with `DRY_RUN=true` and review the log output.
5. Change `DRY_RUN=false` only after confirming the PID list and target OCFL directory are correct.
6. Run the script with `uv`:

```shell
uv run ./ocfl_cleanup_dev.py
```

## Caution

This is a destructive development-cleanup script. With `DRY_RUN=false`, matching OCFL objects are permanently purged.

See `sample.env` for the expected configuration values.

---
