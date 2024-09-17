# Changelog

## v0.3.0

Released on 2024-09-17.

- New command `remove` to remove an entry from the library and its note and PDF files.

## v0.2.1

Released on 2024-09-17.

- Fix version number in the CLI help message.

## v0.2.0

Released on 2024-09-17.

- New CLI option `--version` to show the version number and exit.
- `pdf download` terminal output improved.
- Fix error when downloading PDFs with `pdf download` command.
- `pdf add` command is now working.
- Modify `note` command to only search the location and folder the user provides, does not recursively search.
- Add options `--contents` and  `--file-contents` to `note` command to change the content of the note.
- Fix issue where hidden folders were being shown in the TUI file tree.

## v0.1.0

Released on 2024-09-14.

- Initial release with add, check, export, html, import, init, note, pdf, show and tui commands.
- Some features are not yet implemented or fully functional.
- Some help messages are not fully written.
