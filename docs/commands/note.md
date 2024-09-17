# note

![GIF](../media/note.gif)

Command to **view the note of an entry.**

???+ new "New in v0.2.0"
    - Add the `--contents` option to replace the current note with the provided text.
    - Add the `--file-contents` option to replace the current note with the contents of a file.

## Usage

```bash
bibman note [OPTIONS] NAME
```

## Arguments

* `NAME` The name of the entry to view the note of.

## Options

* `--folder` The folder where the entry is located. If not provided, the program will search the whole library contents and show the first match.
* :material-plus-box:{ .new-color title="New in v0.2.0" } `--contents` Text to replace the current note with.
* :material-plus-box:{ .new-color title="New in v0.2.0" } `--file-contents` Path to a file to replace the current note with.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.