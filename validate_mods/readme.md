# validate MODS

## Purpose

This utility validates a MODS XML file against the XML schema declared in the root MODS element. It is intended for quick local checks before using MODS files in update or ingest workflows.

## What this does

`validate_mods_code.py` reads optional configuration from `../../dot_env_files/validate_mods.env`, parses the supplied MODS XML file, reads its `xsi:schemaLocation`, loads the referenced schema from either a URL or a local file path, and reports whether the XML is valid against that schema.

## Usage

From the `validate_mods` directory:

1. Create the dotenv directory if it does not already exist:

```shell
mkdir -p ../../dot_env_files
```

2. Copy `sample.env` to the script-specific dotenv path:

```shell
cp ./sample.env ../../dot_env_files/validate_mods.env
```

3. Edit `../../dot_env_files/validate_mods.env` if you need to override the schema request timeout:
    - `VM__SCHEMA_REQUEST_TIMEOUT`: optional HTTP timeout in seconds for schema URL requests.
4. Run the script with `uv`:

```shell
uv run ./validate_mods_code.py --mods-path './example_mods/invalid_mods.xml'
```

Run tests with:

```shell
uv run -m unittest ./test_validate_mods_code.py
```

See `sample.env` for the expected configuration values.
