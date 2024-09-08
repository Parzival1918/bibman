# note

![GIF](../media/note.gif)

Command to **view the note of an entry.**

## Usage

```bash
bibman note [OPTIONS] NAME
```

## Arguments

* **NAME** - The name of the entry to view the note of.

## Options

* **--folder** - The folder where the entry is located. If not provided, the program will search the whole library contents and show the first match.
* **--location** - The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.