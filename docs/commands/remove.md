# remove

???+ new "New command in v0.3.0"
    - Remove an entry from the library and its note and PDF files.

**Remove an entry** from the library and its note and PDF files.

## Usage

```bash
bibman remove [OPTIONS] NAME
```

## Arguments

- `NAME` The name of the entry to remove.

## Options

- `--folder` Location of the entry in the library. Default is the root of the library.
- `--yes/--no` Do not ask for confirmation before removing the entry. Default is `--no`.
- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.