# import

**Import the contents** of a `.bib` file into the library. This file can contain one or more entries, but they will all be added to the same folder in the library.

## Usage

```bash
bibman import [OPTIONS] FILE 
```

## Arguments

- `FILE` The path to the `.bib` file to import.

## Options

- `--folder` The folder in the library where the entries will be added. If not provided, the entries will be added to the root of the library.
- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.