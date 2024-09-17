# init

Command to **initialize a new library.** This command creates a new library with the name provided by the `--name` option in the current directory (with default name `references`). The library will have the following structure:

```bash
./
├── .bibman.toml
└── references/
```

## Usage

```bash
bibman init [OPTIONS] 
```

## Options

- `--name` The name of the library. Default is `references`.
- `--git/--no-git` Initialize a git repository in the library. Default is `--no-git`.
- `--location` The location where the library and the `.bibman.toml` file will be created. Default is the current directory (`.`).