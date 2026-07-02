# bdr_scripts_public

## Purpose

Shared public scripts for Brown Digital Repository maintenance and related workflows.

## Installation

```sh
mkdir ./bdr_scripts_public_stuff
cd ./bdr_scripts_public_stuff
git clone git@github.com:Brown-University-Library/bdr_scripts_public.git ./bdr_scripts_public
```

## Usage

Choose the sub-project you want to run, change into that directory, and follow the instructions in that sub-project's README.

```sh
cd ./bdr_scripts_public/<sub-project-name>
cat README.md
```

## Info

Repo for small scripts for different purposes.

Suggestion... we put 50-word-max summaries here, and link to internal READMEs for more info.

- `purge_ocfl`
    - short summary: Destructive development-cleanup utility that purges reviewed BDR PIDs from an OCFL storage root with `rocfl`. Reads target paths from an env file, confirms before work, supports dry-run logging, and should be used only when permanent OCFL deletion is intended.
    - [more info](./purge_ocfl/README.md)

- `save_mods_to_dir`
    - short summary: Downloads MODS XML for a reviewed list of BDR PIDs into a local output directory. Supports configurable URL patterns, request timeouts, logging, and parallel downloads, then checks that each saved MODS file is well-formed XML.
    - [more info](./save_mods_to_dir/README.md)

- `solr_collections`
    - short summary: Queries the BDR public search API with Solr faceting enabled and prints collection names with item counts. Useful for lightweight reporting snapshots or answering collection-count questions without running a larger data export.
    - [more info](./solr_collections/README.md)

- `update_hhoag_mods`
    - short summary: Updates selected Hall-Hoag BDR MODS records from reviewed local MODS files. Maps Hall-Hoag IDs to BDR PIDs through the public API, skips already tracked items, calls a configured update-MODS binary, and writes tracker files outside the repo.
    - [more info](./update_hhoag_mods/README.md)

- `validate_mods`
    - short summary: Validates a MODS XML file against the schema declared in its root element. Reads the `xsi:schemaLocation`, loads the referenced schema from a URL or local path, and reports whether the XML passes validation.
    - [more info](./validate_mods/README.md)

---
