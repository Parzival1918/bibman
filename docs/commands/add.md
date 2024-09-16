# add

![GIF](../media/add.gif)

Command to **add new entries to the library.**

## Usage

```bash
bibman add [OPTIONS] IDENTIFIER
```

## Arguments

* `IDENTIFIER` The identifier of the entry to add. Can be a URL of an article, DOI, PMCID or PMID.

## Options

* `--timeout` The maximum time to wait for the request to complete. Default is 5 seconds.
* `--name` The name of the entry to add. If not provided, the default provided by the source will be used.
* `--folder` The folder to add the entry to. If not provided, the entry will be added to the root folder of the library.
* `--note` A note to add to the entry. If not provided, the entry will have a note with the contents: *"No notes for this entry."*
* `--yes/--no` Skip the confirmation prompt and add the entry immediately. Default is `--no`.
* `--show-entry/--no-show-entry` Show the entry and prompt the user to add it or not to the library. Default is `--show-entry`.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.
