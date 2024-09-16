# show

![GIF](../media/show.gif)

Command to **show the contents of some or all entries in the library.**

## Usage

```bash
bibman show [OPTIONS]
```

## Options

* `--filter-title` Filter the entries by title. The filter is case-insensitive and can be a substring of the title.
* `--filter-entry-types` Filter the entries by type. Multiple types can be provided by calling the option multiple times.
* `--output-format` The format to output the results. You can use the fields: path, title, author, year, month, entry_name, entry_type. Default is `"{path}: {title}"`.
* `--simple-output/--no-simple-output` Overrides the `--output-format` option and sets it to `"{path}"`. Default is `--no-simple-output`.
* `--interactive/--no-interactive` Interactively show the entries using fzf. Default is `--no-interactive`.
* `--fzf-default-opts` The options to pass to fzf. Default is `["-m", "--preview='cat {}'", "--preview-window=wrap"]`.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.