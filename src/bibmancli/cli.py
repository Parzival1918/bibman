import typer
from typing_extensions import Annotated
from typing import Optional, List
from pathlib import Path
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.console import Console
import shutil
from pyfzf import FzfPrompt
from collections.abc import Iterable
from bibmancli.resolve import resolve_identifier
from bibmancli.bibtex import bib_to_string, file_to_bib, file_to_library
from bibmancli.utils import (
    in_path,
    Entry,
    QueryFields,
    iterate_files,
    create_html,
)
from bibmancli.config_file import (
    find_library,
    get_library,
    create_toml_contents,
)
from bibmancli.subcommands import check, pdf
from bibmancli.tui import BibApp
from bibmancli.version import __version__


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
app.add_typer(pdf.app, name="pdf")

console = Console()
err_console = Console(stderr=True)


def version_callback(value: bool):
    """
    Callback to show the version number.
    """
    if value:
        console.print(f"[bold]bibman[/] version [yellow]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def app_callback(
    value: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="Show the version number",
            is_eager=True,
            callback=version_callback,
        ),
    ] = None,
):
    """
    Add app options.

    --version shows the version number.
    """
    pass


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
    download_pdf: Annotated[
        bool, typer.Option(help="Download entry pdf if available")
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
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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
    filter_title: Annotated[
        Optional[str], typer.Option(help="Filter by title")
    ] = None,
    filter_entry_types: Annotated[
        Optional[List[str]], typer.Option(help="Filter by entry type")
    ] = None,
    output_format: Annotated[
        str, typer.Option(help="Output format of the entries")
    ] = "{path}: {title}",  # path, title, author, year, month, entry
    simple_output: Annotated[
        bool, typer.Option(help="Show only the path of the entry")
    ] = False,
    interactive: Annotated[
        bool, typer.Option(help="Use fzf to interactively search the entries")
    ] = False,
    fzf_default_opts: Annotated[
        List[str], typer.Option(help="Default options for fzf")
    ] = [
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
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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
    name: Annotated[
        str, typer.Argument(help="Name of the entry to show the note of")
    ],
    folder: Annotated[
        Optional[str], typer.Option(help="Library location where to search")
    ] = None,
    contents: Annotated[
        Optional[str], typer.Option(help="Replace the note with this content")
    ] = None,
    file_contents: Annotated[
        Optional[Path],
        typer.Option(
            help="Replace the note with the contents of this file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
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
    Show the note associated with an entry or update it.

    NAME is the name of the entry.
    --folder is the location in the library where the note is searched. By default all notes are searched.
    --contents replaces the note with this content.
    --file-contents replaces the note with the contents of this file. If both --contents and --file-contents are provided, --contents takes precedence.
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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

    if folder is None:
        search_location = location
    else:
        folders = folder.split("/")
        search_location: Path = location.joinpath(*folders)

    if not name.endswith(".txt"):
        name = name + ".txt"

    if not name.startswith("."):
        name = "." + name

    note_path = search_location / name
    if not note_path.is_file():
        err_console.print(
            f"[red]Note for '{name}' in '{search_location}' not found![/]"
        )
        raise typer.Exit(1)

    if contents:
        with open(note_path, "w") as f:
            f.write(contents)
        console.print(f"[bold green]Note for '{name}' updated![/]")
    elif file_contents:
        with open(file_contents, "r") as f:
            with open(note_path, "w") as nf:
                nf.write(f.read())
        console.print(f"[bold green]Note for '{name}' updated![/]")

    console.print(note_path.read_text())


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

    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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
    filename: Annotated[
        Optional[str], typer.Option(help="Name of the file to save the entries")
    ],
    rename: Annotated[
        bool,
        typer.Option("--rename/--skip", help="Rename entries with same name"),
    ] = True,
    # check: Annotated[
    #     bool, typer.Option()
    # ] = True,  # If export to file check that the entries can be read without error
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
    --rename/--skip renames entries with the same name. Default is --rename. Otherwise, the entry is skipped.
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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
                    if not rename:
                        err_console.print(
                            "Entry with same name already exists! Skipping..."
                        )
                        continue

                    # Rename entry
                    err_console.print(
                        "Entry with same name already exists! Renaming...",
                        end=" ",
                    )
                    idx = 1
                    original = entry.contents.key
                    while entry.contents.key in entry_names:
                        entry.contents.key = original + "_" + str(idx)
                        idx += 1
                    err_console.print(
                        f"old: {original}, new: {entry.contents.key}"
                    )

                entry_names.append(entry.contents.key)
                f.write(bib_to_string(entry.contents))
                f.write("\n")
    else:
        entry_names = []
        for entry in iterate_files(location):
            if entry.contents.key in entry_names:
                if not rename:
                    err_console.print(
                        "Entry with same name already exists! Skipping..."
                    )
                    continue

                # Rename entry
                err_console.print(
                    "Entry with same name already exists! Renaming...", end=" "
                )
                idx = 1
                original = entry.contents.key
                while entry.contents.key in entry_names:
                    entry.contents.key = original + "_" + str(idx)
                    idx += 1
                err_console.print(f"old: {original}, new: {entry.contents.key}")

            entry_names.append(entry.contents.key)
            console.print(
                Syntax(bib_to_string(entry.contents), "bibtex"), end="\n"
            )


@app.command()
def html(
    folder_name: Annotated[
        str, typer.Option(help="Output folder name, must start with '_'")
    ] = "_site",
    overwrite: Annotated[
        bool, typer.Option(help="Overwrite the folder")
    ] = True,
    launch: Annotated[
        bool, typer.Option(help="Launch the site in the browser")
    ] = False,
    yes: Annotated[bool, typer.Option("--yes/--no")] = False,
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
    --overwrite/--no-overwrite overwrites the folder if it already exists. Default is --overwrite.
    --launch/--no-launch launches the site in the default browser. Default is --no-launch.
    --yes/--no skips the confirmation prompts. Default is --no.
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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

    if not folder_name.startswith("_"):
        err_console.print(
            "[yellow]Provided folder name does not have trailing '_',[/] adding it myself..."
        )
        folder_name = "_" + folder_name

    folder = location / folder_name
    if folder.is_dir():
        err_console.print(f"Folder with name '{folder_name}' already exists!")

        if not overwrite:
            raise typer.Exit(1)

        # Delete previous folder
        if not yes:
            if not Confirm.ask(
                "Do you want to overwrite its contents?", console=console
            ):
                err_console.print("[red]Contents in folder left untouched[/]")
                raise typer.Exit(1)

        shutil.rmtree(folder)

    folder.mkdir(parents=True, exist_ok=True)

    html = create_html(location)

    with open(folder / "index.html", "w") as f:
        f.write(html)

    console.print(f"[bold green]HTML site created in '{folder}'[/]")

    if launch:
        console.print("Launching site in the default browser... ", end="")
        typer.launch(str(folder / "index.html"), wait=False)
        console.print("[bold green]Done![/]")


@app.command(name="import")
def func_import(
    file: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to the .bib file",
        ),
    ],
    folder: Annotated[
        Optional[str], typer.Option(help="Folder where to save the entries")
    ] = None,
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
    Import BibTeX entries from a '.bib' file.

    FILE is the path to the '.bib' file.
    --folder is the folder in the library where the entries will be saved. If not provided, the entries are saved in the root of the library location.
    --location is the directory containing the .bibman.toml file of the library. If not provided, a .bibman.toml file is searched in the current directory and all parent directories.
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

    if not file.name.endswith(".bib"):
        err_console.print(
            f"[bold red]ERROR[/] '{file}' does not have '.bib' extension"
        )

        raise typer.Exit(1)

    bib_library = file_to_library(file)

    if len(bib_library.entries) == 0:
        err_console.print(f"[bold yellow]WARNING[/] No entries found in {file}")
        raise typer.Exit(1)

    if folder is None:
        save_location: Path = location
    else:
        folders = folder.split("/")
        save_location: Path = location.joinpath(*folders)

        # create necessary folders
        save_location.mkdir(parents=True, exist_ok=True)

    for entry in bib_library.entries:
        text = bib_to_string(entry)
        save_path: Path = save_location / (entry.key + ".bib")
        note_path: Path = save_location / ("." + entry.key + ".txt")
        if save_path.is_file():
            err_console.print(
                f"[bold yellow]WARNING[/] File with same name '{entry.key}' already exists! Skipping..."
            )
            continue

        with open(save_path, "w") as f:
            f.write(text)

        with open(note_path, "w") as f:
            f.write("No notes for this entry.")

        console.print(
            f"[bold green]Entry '{entry.key}' saved in '{save_path}'[/]"
        )


@app.command()
def init(
    name: Annotated[
        str, typer.Option(help="Name of the library")
    ] = "references",
    git: Annotated[
        bool, typer.Option(help="Initialize a git repository")
    ] = False,
    location: Annotated[
        Optional[Path],
        typer.Option(
            exists=False,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            help="Location of the library",
        ),
    ] = Path("./"),
):
    """
    Initialize a new library.

    --name is the name of the library.
    --git initializes a git repository in the library. Default is --no-git.
    --location is the location of the library. Default is the current directory.
    """
    lib_location = location / name

    config_file = location / ".bibman.toml"

    if config_file.exists():
        err_console.print(
            "[bold red]ERROR[/] This directory already contains a .bibman.toml file!"
        )
        raise typer.Exit(1)

    if lib_location.exists():
        err_console.print(
            f"[bold red]ERROR[/] Directory with name '{name}' already exists!"
        )
        raise typer.Exit(1)

    lib_location.mkdir(parents=True, exist_ok=True)

    config_file.write_text(create_toml_contents(name))

    console.print(
        f"[bold green]Library '{name}' initialized in '{lib_location}'[/]"
    )

    if git:
        import subprocess

        subprocess.run(["git", "init"], cwd=location)


if __name__ == "__main__":
    app()
