import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from bibman.resolve import send_request
from bibman.bibtex import file_to_bib
from bibtexparser.library import Library


app = typer.Typer(
    no_args_is_help=True,
)


@app.command()
def identifier(
    identifier: Annotated[str, typer.Argument()],
    timeout: Annotated[float, typer.Option(min=1.0)] = 5.0
):
    # check if identifier is valid
    with Progress(SpinnerColumn(), TextColumn(text_format="[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Checking identifier...")
        try:
            r = send_request(identifier, timeout)

            if r.status_code == 200:
                print("Identifier is valid!")
            else:
                print("Identifier is NOT valid")
        except Exception:
            print("Identifier is NOT valid")


@app.command()
def library(
    fix: Annotated[bool, typer.Option()] = False,
    location: Annotated[Path, typer.Option(exists=True,file_okay=False,dir_okay=True,writable=True,
                                           readable=True,resolve_path=True)] = Path.home() / "references",
):
    # check if all entries in library are properly formatted
    with Progress(SpinnerColumn(), TextColumn(text_format="[progress.description]{task.description}"), transient=True) as progress:
        for root, dirs, files in location.walk():
            if root.name.startswith("_"):
                # skip _site folder
                continue

            for name in files:
                filepath = root / name
                progress.add_task(description=f"Checking {filepath}")

                if name.startswith(".") and name.endswith(".txt"): # possible note 
                    # check if file exists with same name but .bib extension
                    bib_name = name[1:-4] + ".bib"
                    bib_file = root / bib_name
                    if not bib_file.is_file():
                        print(f"Note file found that does not have an entry file associated: {name}")
                    else:
                        print(f"{filepath}: Note with matching entry found")
                    continue


                if not name.endswith(".bib"):
                    print(f"Found file that is not of .bib extension: {filepath}")

                # check that bib file is valid
                bib_library: Library = file_to_bib(filepath)

                if len(bib_library.entries) > 1:
                    print(f"Found file that contains multiple BibTeX entries: {filepath}")
                
                print(f"{filepath}: No warnings raised")

            
