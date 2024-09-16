# Install

I would recommend using [`pipx`](https://github.com/pypa/pipx) to install `bibman`:

```bash
> pipx install bibmancli
```

Alternatively, you can install it using `pip`:

```bash
> pip install bibmancli
```

This will install the `bibman` CLI. Go to [Commands](./commands/add.md) to see the available commands.

!!! warning

    - The package uses a pre-release version of `bibtexparser`. This may cause issues with the installation (e.g. I can't install it using rye).
    - The `pip` installation method is not recommended as it may cause conflicts with other packages. `pipx` creates a virtual environment for the package and installs it there to avoid conflicts.
    - The CLI is still in development and may have bugs. Please report any issues you encounter.
