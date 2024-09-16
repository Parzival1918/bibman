# pdf

Add or download PDFs to your library entries.

## Usage

```bash
bibman pdf [OPTIONS] COMMAND [ARGS]... 
```

## Commands

### add

Add a PDF file to an entry in the library.

#### Usage

```bash
bibman pdf add [OPTIONS] ENTRY PDF
```

#### Arguments

- `ENTRY` The identifier of the entry to add the PDF to.
- `PDF` The path to the PDF file to add.

#### Options

- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.

### download

Try to download the PDF files of all entries in the library.

#### Usage

```bash
bibman pdf download [OPTIONS]
```

#### Options

- `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.
