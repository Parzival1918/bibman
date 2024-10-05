# Changelog

## v0.3.2

Released on 2024-10-05.

- `check library` command now ignores the `.git` and `.github` folders, and `.gitignore` file.
- Modify html output of `html` command.
    - Margins are smaller in mobile devices.
    - Can now show entries by folder.
- In the TUI, the editor for the entry and note is taken from the `EDITOR` environment variable. If not set, it raises a warning.

Pypi: https://pypi.org/project/bibmancli/0.3.2/