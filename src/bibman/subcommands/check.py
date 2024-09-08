import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from typing import Optional
from bibman.resolve import send_request
from bibman.bibtex import file_to_bib
from bibtexparser.library import Library
from bibman.config_file import find_library, get_library


app = typer.Typer(
    no_args_is_help=True,
    help="""
    Check the validity of an identifier, or check if all entries in a library are properly formatted.
    """,
)

console = Console()
err_console = Console(stderr=True)


@app.command()
def identifier(
    identifier: Annotated[str, typer.Argument(help="Identifier of the entry")],
    timeout: Annotated[
        float, typer.Option(min=1.0, help="Request timeout in seconds")
    ] = 5.0,
):
    """
    Check if an identifier is valid.

    IDENTIFIER can be URL of an article, DOI, PMCID or PMID.
    --timeout is the time in seconds to wait for a response. Default is 5.0.
    """
    # check if identifier is valid
    with Progress(
        SpinnerColumn(),
        TextColumn(text_format="[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task(description="Checking identifier...")
        try:
            r = send_request(identifier, timeout)

            if r.status_code == 200:
                console.print("[green]Identifier is valid![/]")
            else:
                err_console.print("[bold red]ERROR[/] Identifier is NOT valid")
        except Exception:
            print("Identifier is NOT valid")


@app.command()
def library(
    fix: Annotated[
        bool,
        typer.Option(
            "--fix/--ignore", help="Try to fix any problems identified"
        ),
    ] = False,
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
    Check if all entries in the library are properly formatted.

    If --fix is provided, will attempt to fix any issues found. Mainly removing files that are not managed by bibman.
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

    # check if all entries in library are properly formatted
    for root, dirs, files in location.walk():
        if root.name.startswith("_"):
            # skip _site folder
            continue

        for name in files:
            filepath = root / name

            if name.startswith(".") and name.endswith(".txt"):  # possible note
                # check if file exists with same name but .bib extension
                bib_name = name[1:-4] + ".bib"
                bib_file = root / bib_name
                if not bib_file.is_file():
                    console.print(
                        f"[red]Note file found that does not have an entry file associated[/]: {name}"
                    )
                    if fix:
                        console.print(
                            " |-> Removing note file...",
                            end="",
                        )
                        filepath.unlink()
                        console.print(" [green]Done[/]")
                else:
                    console.print(
                        f"{filepath}: [green]Note with matching entry found[/]"
                    )
                continue

            if not name.endswith(".bib"):
                console.print(
                    f"[red]Found file that is not managed by bibman:[/] {filepath}"
                )

                if fix:
                    console.print(
                        " |-> Removing file...",
                        end="",
                    )
                    filepath.unlink()
                    console.print(" [green]Done[/]")

            # check that bib file is valid
            bib_library: Library = file_to_bib(filepath)

            if len(bib_library.entries) > 1:
                console.print(
                    f"[red]Found file that contains multiple BibTeX entries[/]: {filepath}"
                )

            console.print(f"{filepath}: [green]No warnings raised[/]")
