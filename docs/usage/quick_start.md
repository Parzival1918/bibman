# Quick start

`bibman` is a simple tool to manage your bibliography in **BibTeX format**. It saves your entries in individual `.bib` files in your *library*. The tool automatically looks for a [config file (`.bibman.toml`)](../config-format/index.md) in the current directory and its parent directories to find the location of your library, but you can override the search with the `--location` option. This means that you can manage multiple libraries in different directories. So you can manage references for different projects!

## Initial setup

To get started first [install the tool](../install.md) and then create a library with the following command:

```bash
bibman init
```

This will create a new directory and file:

```bash
./
├── .bibman.toml
└── references/
```

The `.bibman.toml` file is the configuration file for the library. It contains the path to the library and other settings. The `references/` directory is where your `.bib` files will be stored.

Ideally you should not manually move or edit files in the `references/` directory. Instead, use the `bibman` commands to manage your bibliography. In case you do any manual changes, you can always run `bibman check library` to check for any inconsistencies in your library.

## Adding references to the library

Now we can start adding references to our library. You can add references from a `.bib` file or using the entry identifier.

=== "From a `.bib` file"
    To import references from a `.bib` file, use the following command:

    ```bash
    bibman import PATH_TO_BIB_FILE
    ```

    This will add all the entries in the file to your library.

=== "Identifier"
    To add references with the entry identifier, use the following command:

    ```bash
    bibman add IDENTIFIER
    ```

    This will search the entry information online and prompt you to confirm the entry before adding it to your library.

## Exporting references

You may want to use this tool to manage the citations for a LaTeX document. In order to merge all the references into a single `.bib` file, you can use the following command:

```bash
bibman export --filename FILENAME
```

This will create a new `.bib` with name `FILENAME` in the current directory.

## Viewing references

A CLI interface might not be the easiest way to filter and view the entries in your library, but you still can do so:

```bash
bibman show
```

This will display the path and title of all the entries in your library. If you have `fzf` installed, you can search and filter the entries interactively using the following command:

```bash
bibman show --interactive
```

But this tool includes the possibility to create a simple html page with all the entries in your library in which you can fuzzy search and filter the entries. To create this page and open it in your browser, use the following command:

```bash
bibman html --launch
```

Using this command you can upload the library to GitHub and use it to host your references online, a sample GitHub workflow is shown in [here](../commands/html.md).