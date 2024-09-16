# bibman

<center>

[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://rye.astral.sh)
![GitHub License](https://img.shields.io/github/license/parzival1918/bibman)

![PyPI - Version](https://img.shields.io/pypi/v/bibmancli)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bibmancli)

</center>

A CLI utility to manage references in BibTeX format. See the [documentation](https://parzival1918.github.io/bibman/) for more information.

![Main GIF](./tapes/main.gif)

Check my references managed using this tool and hosted in GitHub Pages [here](https://parzival1918.github.io/references/).

## Installation

I would recommend using [`pipx`](https://github.com/pypa/pipx) to install `bibman`:

```bash
> pipx install bibmancli
```

Alternatively, you can install it using `pip`:

```bash
> pip install bibmancli
```

This will install the `bibman` CLI.

> [!WARNING]
> - The package uses a pre-release version of `bibtexparser`. This may cause issues with the installation (e.g. I can't install it using rye).
> - The `pip` installation method is not recommended as it may cause conflicts with other packages. `pipx` creates a virtual environment for the package and installs it there to avoid conflicts.
> - The CLI is still in development and may have bugs. Please report any issues you encounter.
