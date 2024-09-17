# export

![GIF](../media/export.gif)

Command to **export the library contents to a file.**

Entries with same name but in different folders of the library will be ignored and only the first one found will be exported.

## Usage

```bash
bibman export [OPTIONS] 
```

## Options

* `--filename` The name of the file to export the library to.
* `--rename/--skip` Rename the file if it already exists. Default is to skip it.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.