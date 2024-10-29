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

## Nix Flakes

???+ new "New in v0.3.1"
    - Added Flake to use with nix package manager.
    - Git hash of v0.3.1 is: 51a05e0ea3388617f87d19bb0aaee01e30726df6
    - Git hash of v0.3.2 is: 51c45bfd6c60b0654e84f327531f9cf6696e5ba2
    - Git hash of v0.3.3 is: cc05a07074e4e52f23675b921d8389922e1a2c44

Since v0.3.1 this repository also includes a Nix Flake to install the application. You can use it by adding to your Flake inputs:

```nix
inputs.bibman.url = "github:parzival1918/bibman/cc05a07074e4e52f23675b921d8389922e1a2c44";
```

and the following to your system or user packages:

```nix
[
    (...)
    inputs.bibman.packages.${systemArch}.bibman
    (...)
];
```

!!! warning

    - The package uses a pre-release version of `bibtexparser`. This may cause issues with the installation (e.g. I can't install it using rye).
    - The `pip` installation method is not recommended as it may cause conflicts with other packages. `pipx` creates a virtual environment for the package and installs it there to avoid conflicts.
    - The CLI is still in development and may have bugs. Please report any issues you encounter.
