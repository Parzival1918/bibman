# tui

![GIF](../media/tui.gif)

Command to **enter a TUI to interact with the library.**

You can view the entries and their notes, as well as edit them.

???+ warning "Bug in v0.1.0"
    The file tree in the TUI shows hidden folders. This is fixed in [v0.2.0](../changelog.md#v020).

## Usage

```bash
bibman tui [OPTIONS]
```

## Options

* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.