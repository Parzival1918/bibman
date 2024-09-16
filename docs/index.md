# bibman

![Main GIF](./media/main.gif)

<center>

[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://rye.astral.sh)
![GitHub License](https://img.shields.io/github/license/parzival1918/bibman)

![PyPI - Version](https://img.shields.io/pypi/v/bibmancli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bibmancli)

</center>

Bibman is a simple tool to manage your bibliography in **BibTeX format**. It saves your entries in individual `.bib` files in your library.

The tool automatically looks for a [config file (`.bibman.toml`)](./config-format/index.md) in the current directory and its parent directories to find the location of your library, but you can override the search with the `--location` CLI option. This means that you can manage multiple libraries in different directories.

The CLI uses [Typer](https://typer.tiangolo.com) to provide a visually pleasing interface and include shell completion.

Check the [Quick start](./usage/quick_start.md) guide to get started with bibman.

## Features

- Add, remove, and list entries in your library.
- Search for entries by title, author, or year. Or **use fzf to search interactively**.
- **Export all your library contents** to a single `.bib` file.
- **Add notes** to your entries.
- Create a **simple html page** to view your library contents and search interactively. Check my references created using this command and hosted in GitHub Pages [here](https://parzival1918.github.io/references/).
