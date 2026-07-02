# Purpose

## What this does

`ocfl_cleanup_dev.py` deletes OCFL objects for a supplied list of BDR PIDs.

The script reads configuration from a `.env` file, including the OCFL directory,
the `rocfl` command path, a log-file path, a PID-list file, and `DRY_RUN`.
It prompts before doing any work, changes into the configured OCFL directory,
then checks each PID with `rocfl ls`.

When `DRY_RUN` is set to `true`, the script logs the purge command that would
run. When `DRY_RUN` is set to `false`, it runs `rocfl purge <pid> --force` for
each PID found in the OCFL storage.

## Caution

This is a destructive development-cleanup script. With `DRY_RUN=false`, matching
OCFL objects are permanently purged.

See `sample_dot_env` for the expected configuration values.

---
