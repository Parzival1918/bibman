# check

![GIF](../media/check.gif)

Command to **check the validity of an identifier or the library contents.**

## Usage

```bash
bibman check [OPTIONS] COMMAND [ARGS]...
```

## Commands

### identifier

#### Usage

```bash
bibman check identifier [OPTIONS] IDENTIFIER
```

#### Arguments

* `IDENTIFIER` The identifier of the entry to add. Can be a URL of an article, DOI, PMCID or PMID.

#### Options

* `--timeout` The maximum time to wait for the request to complete. Default is 5 seconds.

### library

#### Usage

```bash
bibman check library [OPTIONS]
```

#### Options

* `--fix/--ignore` Attempt to fix any issues found. Mainly removing files that are not managed by bibman. Default is `--ignore`.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.