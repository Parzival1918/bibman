import typer
from typing_extensions import Annotated
from typing import Optional, List
from pathlib import Path
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.console import Console
from pyfzf import FzfPrompt
from collections.abc import Iterable
from bibman.resolve import resolve_identifier
from bibman.bibtex import bib_to_string, file_to_bib
from bibman.utils import in_path, Entry, QueryFields, iterate_files, create_html
from bibman.config_file import find_library, get_library
from bibman.subcommands import check
from bibman.tui import BibApp


app = typer.Typer(
    name="bibman",
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="""
        Simple CLI tool to manage [bold]BibTeX[/] files.
    """,
    epilog="""
        by [bold]Pedro Juan Royo[/] (http://pedro-juan-royo.com)
    """,
)
app.add_typer(check.app, name="check")

console = Console()
err_console = Console(stderr=True)


@app.command()
def add(
    identifier: Annotated[str, typer.Argument(help="Identifier of the entry")],
    timeout: Annotated[
        float, typer.Option(min=1.0, help="Request timeout in seconds")
    ] = 5.0,
    name: Annotated[Optional[str], typer.Option(help="Name of file")] = None,
    folder: Annotated[
        Optional[str],
        typer.Option(help="Save location relative to the library location"),
    ] = None,
    note: Annotated[
        str, typer.Option(help="Notes attached to this entry")
    ] = "No notes for this entry.",
    yes: Annotated[bool, typer.Option("--yes/--no")] = False,
    show_entry: Annotated[
        bool, typer.Option(help="Show the fetched BibTeX entry.")
    ] = True,
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Add a new BibTeX entry to the library.

    IDENTIFIER can be a URL of an article, DOI, PMCID or PMID.
    --timeout is the time in seconds to wait for the request. Default is 5 seconds.
    --name is the name of the file to save the entry. If not provided, the key of the entry is used.
    --folder is the folder where the entry will be saved. If not provided, the file is saved in the root of the library location.
    --note is a note to save with the entry. Default is "No notes for this entry."
    --yes skips the confirmation prompts. Default is --no.
    --show-entry shows the entry before saving it. Defaults to show the entry.
    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn(text_format="[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        # get the bibtex citation
        progress.add_task(
            description=f"Searching BibTeX entry for {identifier}..."
        )
        bibtex_library = resolve_identifier(identifier, timeout)

    # select the citation entry from the BibDatabase
    entry = bibtex_library.entries[0]
    text = bib_to_string(bibtex_library)

    if show_entry:
        console.print(Syntax(text, "bibtex"))
        if not yes:
            if not Confirm.ask("Do you accept this entry?", console=console):
                err_console.print("[red]Entry rejected[/]")
                raise typer.Exit(1)

    # check the --folder option
    if folder is None:
        save_location: Path = location
    else:
        folders = folder.split("/")
        save_location: Path = location.joinpath(*folders)

        # create necessary folders
        save_location.mkdir(parents=True, exist_ok=True)

    # Save the citation
    if name is None:
        save_name = entry.key + ".bib"
        note_name = "." + entry.key + ".txt"
    else:
        if name.endswith(".bib"):
            save_name = name
            note_name = "." + name.replace(".bib", ".txt")
        else:
            save_name = name + ".bib"
            note_name = "." + name + ".txt"

    # save entry and note
    save_path: Path = save_location / save_name
    if save_path.is_file():
        err_console.print("File with same name already exists!")
        raise typer.Exit(1)

    note_path: Path = save_location / note_name
    if note_path.is_file():
        err_console.print("Note with same name already exists!")
        raise typer.Exit(1)

    with open(save_path, "w") as f:
        f.write(text)

    with open(note_path, "w") as f:
        f.write(note)


@app.command()
def show(
    filter_title: Annotated[Optional[str], typer.Option()] = None,
    filter_entry_types: Annotated[Optional[List[str]], typer.Option()] = None,
    output_format: Annotated[
        str, typer.Option()
    ] = "{path}: {title}",  # path, title, author, year, month, entry
    simple_output: Annotated[bool, typer.Option()] = False,
    interactive: Annotated[bool, typer.Option()] = False,
    fzf_default_opts: Annotated[List[str], typer.Option()] = [
        "-m",
        "--preview='cat {}'",
        "--preview-window=wrap",
    ],
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Show the entries in the library.

    --filter-title filters the entries by title.
    --filter-entry-types filters the entries by type. For example, 'article', 'book', 'inproceedings', etc.
    --output-format is the format of the output. Default is "{path}: {title}". Available fields are: path, title, author, year, month, entry_name, entry_type.
    --simple-output shows only the path of the entry. Overrides --output-format, setting it to "{path}".
    --interactive uses fzf to interactively search the entries.
    --fzf-default-opts are the default options for fzf. Defaults are ["-m", "--preview='cat {}'", "--preview-window=wrap"].
    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    if simple_output:  # overrides output_format
        output_format = "{path}"

    # filters
    filter_dict = {
        QueryFields.TITLE.name: filter_title,
        QueryFields.ENTRY.name: filter_entry_types,
    }

    # load the citations in --location
    # maybe more efficient to put in a function and yield the results
    if not interactive:
        for entry in iterate_files(location):
            if entry.apply_filters(filter_dict):
                console.print(entry.format_string(output_format))
    else:  # interactive with fzf
        if in_path("fzf"):

            def fzf_func() -> Iterable[Entry]:
                for entry in iterate_files(location):
                    if entry.apply_filters(filter_dict):
                        yield str(entry.path)

            fzf = FzfPrompt(default_options=fzf_default_opts)
            result_paths = fzf.prompt(fzf_func())
            for path in result_paths:
                entry = Entry(Path(path), file_to_bib(Path(path)).entries[0])
                console.print(entry.format_string(output_format))
        else:
            err_console.print("Error fzf not in path")
            raise typer.Exit(1)


@app.command()
def note(
    name: Annotated[str, typer.Argument(help="Name of the entry to show the note of")],
    # edit: Annotated[bool, typer.Option()] = False,
    # interactive: Annotated[bool, typer.Option()] = False,
    # fzf_default_opts: Annotated[List[str], typer.Option()] = [
    #     "-m",
    #     "--preview='cat {}'",
    #     "--preview-window=wrap",
    # ],
    folder: Annotated[Optional[str], typer.Option(help="Library location where to search")] = None,
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Show the note associated with an entry.

    NAME is the name of the entry.
    --folder is the location in the library where the note is searched. By default all notes are searched.
    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    # --edit opens the note in an editor.
    # --interactive uses fzf to interactively search the entries.
    # --fzf-default-opts are the default options for fzf. Defaults are ["-m", "--preview='cat {}'", "--preview-window=wrap"].
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    if folder is None:
        search_location = location
    else:
        folders = folder.split("/")
        search_location: Path = location.joinpath(*folders)

    if not name.endswith(".txt"):
        name = name + ".txt"

    if not name.startswith("."):
        name = "." + name

    # if not interactive:
    for root, _, files in search_location.walk():
        for filename in files:
            if filename == name:
                # process file
                # if not edit:
                filepath = root / filename
                contents = filepath.read_text()
                console.print(contents)
                raise typer.Exit(0)
    
    err_console.print("[red]Note not found![/]")
    raise typer.Exit(1)
    # else:
    #     if in_path("fzf"):
    #         pass
    #         # fzf = FzfPrompt(default_options=fzf_default_opts)
    #         # result_paths = fzf.prompt(_show_func_fzf(location, filter_dict))
    #         # print(result_paths)
    #     else:
    #         err_console.print("Error fzf not in path")
    #         raise typer.Exit(1)


@app.command()
def tui(
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Open the TUI interface to manage the library.

    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    app = BibApp(location=location)
    app.run()


@app.command()
def export(
    filename: Annotated[Optional[str], typer.Option()] = None,
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Export the BibTeX entries.

    --filename is the name of the file to save the entries. If not provided, set by default, the entries are printed to the console.
    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    if filename:
        filepath: Path = Path(filename)
        if filepath.is_file():
            err_console.print(f"File with name '{filename}' already exists!")
            raise typer.Exit(1)

        # must check that there are no repeated entry names
        entry_names = []
        with open(filepath, "w") as f:
            for entry in iterate_files(location):
                if entry.contents.key in entry_names:
                    err_console.print(
                        "Entry with same name already exists! Skipping..."
                    )
                    continue

                entry_names.append(entry.contents.key)
                f.write(bib_to_string(entry.contents))
                f.write("\n")
    else:
        entry_names = []
        for entry in iterate_files(location):
            if entry.contents.key in entry_names:
                err_console.print(
                    "Entry with same name already exists! Skipping..."
                )
                continue

            entry_names.append(entry.contents.key)
            console.print(
                Syntax(bib_to_string(entry.contents), "bibtex"), end="\n"
            )


@app.command()
def html(
    folder_name: Annotated[
        str, typer.Option(help="Output folder name")
    ] = "_site",
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Directory containing the .bibman.toml file",
        ),
    ] = None,
):
    """
    Create a simple HTML site with the BibTeX entries.

    --folder-name is the name of the folder where the site will be created. Default is '_site'.
    --location is the direcotry containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
    """
    if location is None:
        location = find_library()
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in current directory or parents!"
            )
            raise typer.Exit(1)
    else:
        location = get_library(location)
        if location is None:
            err_console.print(
                "[bold red]ERROR[/] .bibman.toml not found in the provided directory!"
            )
            raise typer.Exit(1)

    folder = location / folder_name
    if folder.is_dir():
        err_console.print(f"Folder with name '{folder_name}' already exists!")
        raise typer.Exit(1)

    folder.mkdir(parents=True, exist_ok=True)

    html = create_html(location)

    with open(folder / "index.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    app()
