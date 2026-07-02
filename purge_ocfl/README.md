# ocfl cleanup script

## Purpose

This development utility removes known test or cleanup objects from an OCFL
storage root by BDR PID. It is intended for controlled cleanup work where the
PID list has already been reviewed and the caller explicitly wants matching
OCFL objects purged with `rocfl`.

## What this does

`ocfl_cleanup_dev.py` deletes OCFL objects for a supplied list of BDR PIDs.

The script reads configuration from a `.env` file, including the OCFL directory,
the `rocfl` command path, a log-file path, a PID-list file, and `DRY_RUN`.
It prompts before doing any work, changes into the configured OCFL directory,
then checks each PID with `rocfl ls`.

When `DRY_RUN` is set to `true`, the script logs the purge command that would
run. When `DRY_RUN` is set to `false`, it runs `rocfl purge <pid> --force` for
each PID found in the OCFL storage.

## Usage

From the `purge_ocfl` directory:

1. Copy `sample_dot_env` to `.env`.
2. Edit `.env` so these values point to the cleanup target:
    - `OCFL_DIR`: OCFL storage directory to inspect and purge from.
    - `ROCFL_CMD`: path to the `rocfl` executable.
    - `LOG_FILE`: file where cleanup activity should be logged.
    - `PIDS_FILE`: text file containing one BDR PID per line.
    - `DRY_RUN`: set to `true` to log intended purge commands, or `false` to
      permanently purge matching OCFL objects.
3. Start with `DRY_RUN=true` and review the log output.
4. Change `DRY_RUN=false` only after confirming the PID list and target OCFL
   directory are correct.
5. Run the script with `uv`:

```shell
uv run --with python-dotenv ./ocfl_cleanup_dev.py
```

## Caution

This is a destructive development-cleanup script. With `DRY_RUN=false`, matching
OCFL objects are permanently purged.

See `sample_dot_env` for the expected configuration values.

---
