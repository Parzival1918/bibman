# Introduction

![Main GIF](./media/main.gif)

Bibman is a simple tool to manage your bibliography in **BibTeX format**. It saves your entries in individual `.bib` files in your library. 

The tool automatically looks for a config file (`.bibman.toml`) in the current directory and its parent directories to find the location of your library, but you can override the search with the `--location` CLI option. This means that you can manage multiple libraries in different directories.

The CLI uses [Typer](https://typer.tiangolo.com) to provide a visually pleasing interface and include shell completion.

## Features

- Add, remove, and list entries in your library.
- Search for entries by title, author, or year. Or **use fzf to search interactively**.
- **Export all your library contents** to a single `.bib` file.
- **Add notes** to your entries.
- Create a **simple html page** to view your library contents and search interactively.
