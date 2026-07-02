# Solr collections

## Purpose

This utility reports BDR collection names and item counts from the public search API. It is intended for lightweight collection-count snapshots that can answer common BDR reporting questions.

## What this does

`collections_list.py` reads optional configuration from `../../dot_env_files/solr_collections.env`, queries the configured BDR search API with Solr faceting enabled, extracts counts for the configured collection facet field, and prints a two-column table of collection names and item counts.

## Usage

From the `solr_collections` directory:

1. Create the dotenv directory if it does not already exist:

```shell
mkdir -p ../../dot_env_files
```

2. Copy `sample.env` to the script-specific dotenv path:

```shell
cp ./sample.env ../../dot_env_files/solr_collections.env
```

3. Edit `../../dot_env_files/solr_collections.env` if you need to override the defaults:
    - `SC__BDR_API_URL`: BDR search API endpoint to query.
    - `SC__COLLECTION_FIELD`: Solr facet field containing collection names.
    - `SC__LOGLEVEL`: optional log level, usually `INFO` or `DEBUG`.
    - `SC__REQUEST_TIMEOUT`: optional HTTP timeout in seconds.
4. Run the script with `uv`:

```shell
uv run ./collections_list.py
```

See `sample.env` for the expected configuration values.
