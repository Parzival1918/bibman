import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path
from bibman.resolve import resolve_identifier, send_request
from bibman.bibtex import dict_to_bibtex_string


app = typer.Typer(
    name="bibman",
    no_args_is_help = True,
)


@app.command()
def add(
    identifier: Annotated[str, typer.Argument()],
    timeout: Annotated[float, typer.Option(min=1.0)] = 5.0,
    name: Annotated[Optional[str], typer.Option()] = None,
    folder: Annotated[Optional[str], typer.Option()] = None,
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
    ):
    # get the bibtex citation
    bibtex_dict = resolve_identifier(identifier, timeout)

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
        save_name = bibtex_dict["ID"] + ".bib"
    else:
        if name.endswith(".bib"):
            save_name = name
        else:
            save_name = name + ".bib"

    save_path: Path = save_location / save_name
    if save_path.is_file():
        print("File with same name already exists!")
        typer.Exit(1)

    text = dict_to_bibtex_string(bibtex_dict)
    with open(save_path, 'w') as f:
        f.write(text)


@app.command()
def show(
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
    ):
    pass


@app.command(name="import")
def func_import(
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
    ):
    pass




@app.command()
def check(
    identifier: Annotated[str, typer.Argument()],
    timeout: Annotated[float, typer.Option(min=1.0)] = 5.0
    ):
    # check if identifier is valid
    r = send_request(identifier, timeout)

    if r.status_code == 200:
        print("Identifier is valid!")
    else:
        print("Identifier is NOT valid")


if __name__ == "__main__":
    app()
