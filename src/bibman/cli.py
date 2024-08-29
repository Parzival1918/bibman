import typer
from typing_extensions import Annotated
from typing import Optional, List
from pathlib import Path
from rich import print as rprint
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from pyfzf import FzfPrompt
from bibman.resolve import resolve_identifier
from bibman.bibtex import bib_to_string, file_to_bib
from bibman.utils import in_path, Entry, QueryFields
from bibman.subcommands import check


app = typer.Typer(
    name="bibman",
    no_args_is_help = True,
    rich_markup_mode="rich",
    epilog="""
        by [bold]Pedro Juan Royo[/] (http://pedro-juan-royo.com)
    """,
)
app.add_typer(check.app, name="check")


@app.command()
def add(
    identifier: Annotated[str, typer.Argument()],
    timeout: Annotated[float, typer.Option(min=1.0)] = 5.0,
    name: Annotated[Optional[str], typer.Option()] = None,
    folder: Annotated[Optional[str], typer.Option()] = None,
    note: Annotated[str, typer.Option()] = "No notes for this entry.",
    yes: Annotated[bool, typer.Option()] = False,
    show_entry: Annotated[bool, typer.Option()] = True,
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
):
    with Progress(SpinnerColumn(), TextColumn(text_format="[progress.description]{task.description}"), transient=True) as progress:
        # get the bibtex citation
        progress.add_task(description=f"Searching BibTeX entry for {identifier}...")
        bibtex = resolve_identifier(identifier, timeout)

    # select the citation entry from the BibDatabase
    entry = bibtex.entries[0]
    text = bib_to_string(bibtex)

    if show_entry:
        rprint(text)
        if not yes:
            if not Confirm.ask("Do you accept this entry?"):
                print("Entry rejected")
                raise typer.Exit(3)

    # check the --folder option
    if folder is None:
        save_location: Path = location
    else:
        folders = folder.split("/")
        save_location: Path = location.joinpath(*folders)

        # create necessary folders
        save_location.mkdir(parents=True,exist_ok=True)

    # Save the citation
    if name is None:
        save_name = entry["ID"] + ".bib"
        note_name = "." + entry["ID"] + ".txt"
    else:
        if name.endswith(".bib"):
            save_name = name
            note_name = "." + name.replace(".bib", ".txt")
        else:
            save_name = name + ".bib"
            note_name = "." + entry["ID"] + ".txt"

    # save entry and note
    save_path: Path = save_location / save_name
    if save_path.is_file():
        print("File with same name already exists!")
        raise typer.Exit(1)

    note_path: Path = save_location / note_name
    if note_path.is_file():
        print("Note with same name already exists!")
        raise typer.Exit(1)
   
    with open(save_path, 'w') as f:
        f.write(text)

    with open(note_path, 'w') as f:
        f.write(note)


def _show_func(location: Path, filters: dict) -> Entry:
    for root, dirs, files in location.walk():
        for name in files:
            if name.endswith(".bib"): # only count bib files
                file = root / name

                # read the file contents
                bib = file_to_bib(file)

                entry = Entry(file, bib)

                if entry.apply_filters(filters):
                    yield entry


def _show_func_fzf(location: Path, filters: dict) -> Entry:
    for entry in _show_func(location, filters):
        yield str(entry.path)


@app.command()
def show(
    filter_title: Annotated[Optional[str], typer.Option()] = None,
    filter_entry_types: Annotated[Optional[List[str]], typer.Option()] = None,
    output_format: Annotated[str, typer.Option()] = "{path}: {title}", # path, title, author, year, month, entry
    simple_output: Annotated[bool, typer.Option()] = False, 
    interactive: Annotated[bool, typer.Option()] = False,
    fzf_default_opts: Annotated[List[str], typer.Option()] = ["-m", "--preview='cat {}'", "--preview-window=wrap"],
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
):
    if simple_output: # overrides output_format
        output_format = "{path}"

    # filters
    filter_dict = {
        QueryFields.TITLE.name: filter_title,
        QueryFields.ENTRY.name: filter_entry_types, 
    }

    # load the citations in --location
    # maybe more efficient to put in a function and yield the results 
    if not interactive:
        for entry in _show_func(location, filter_dict):
            print(entry.format_string(output_format))
    else: # interactive with fzf
        if in_path("fzf"):
            fzf = FzfPrompt(default_options=fzf_default_opts)
            result_paths = fzf.prompt(_show_func_fzf(location, filter_dict))
            print(result_paths)
        else:
            print("Error fzf not in path")
            raise typer.Exit(2)


@app.command()
def note(
    name: Annotated[str, typer.Argument()],
    edit: Annotated[bool, typer.Option()] = False,
    interactive: Annotated[bool, typer.Option()] = False,
    fzf_default_opts: Annotated[List[str], typer.Option()] = ["-m", "--preview='cat {}'", "--preview-window=wrap"],
    folder: Annotated[Optional[str], typer.Option()] = None,
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
):
    if folder is None:
        search_location = location
    else:
        folders = folder.split("/")
        search_location: Path = location.joinpath(*folders)

    if not name.endswith(".txt"):
        name = name + ".txt"

    if not interactive:
        for root, dirs, files in search_location.walk():
            for filename in files:
                if filename == name:
                    # process file
                    if not edit:
                        filepath = root / filename
                        contents = filepath.read_text()
                        print(contents)
    else:
        if in_path("fzf"):
            pass
            # fzf = FzfPrompt(default_options=fzf_default_opts)
            # result_paths = fzf.prompt(_show_func_fzf(location, filter_dict))
            # print(result_paths)
        else:
            print("Error fzf not in path")
            raise typer.Exit(2)    


# @app.command(name="import")
# def func_import(
#     location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
#                                            readable=True,resolve_path=True)] = Path.home() / "references",
# ):
#     pass


if __name__ == "__main__":
    app()
