# pdf

Add or download PDFs to your library entries.

## Usage

```bash
bibman pdf [OPTIONS] COMMAND [ARGS]... 
```

## Commands

### add

Add a PDF file to an entry in the library.

???+ new "New in v0.2.0"
    - This command is now working.
    - Add the `--folder` option to specify the folder where the entry is located.
    - Add the `--yes/--no` option to skip any confirmation prompts.

#### Usage

```bash
bibman pdf add [OPTIONS] ENTRY PDF_FILE
```

#### Arguments

- :material-plus-box:{ .new-color title="New in v0.2.0" } `ENTRY` The identifier of the entry to add the PDF to.
- :material-plus-box:{ .new-color title="New in v0.2.0" } `PDF_FILE` The path to the PDF file to add.

#### Options

- :material-plus-box:{ .new-color title="New in v0.2.0" } `--folder` The folder where the entry is located.
- :material-plus-box:{ .new-color title="New in v0.2.0" } `--yes/--no` Skip any confirmation prompts. Default is `--no`.
- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.

### download

Try to download the PDF files of all entries in the library.

#### Usage

```bash
bibman pdf download [OPTIONS]
```

#### Options

- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.
