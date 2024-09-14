import typer
from typing_extensions import Annotated
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from typing import Optional
from bibmancli.resolve import send_request
from bibmancli.bibtex import file_to_bib
from bibtexparser.library import Library
from bibmancli.config_file import find_library, get_library


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

    # check if all entries in library are properly formatted
    entry_count = 0
    error_count = 0
    for root, dirs, files in location.walk():
        if root.name.startswith("_"):
            # skip _site folder
            continue

        for name in files:
            filepath = root / name

            if not name.endswith(".bib"):
                # check that file is either .txt or .pdf
                if not name.endswith(".txt") and not name.endswith(".pdf"):
                    console.print(
                        f":red_circle: [red]Found file that is not managed by bibman[/]: {filepath}"
                    )

                    error_count += 1

                    if fix:
                        console.print(
                            "  :arrow_forward: Removing file...",
                            end="",
                        )
                        filepath.unlink()
                        console.print(" [green]Done[/]")

                # if file id .txt or .pdf, check if there is a corresponding .bib file
                if name.endswith(".txt"):
                    entryname = f"{name[1:-4]}.bib"
                    entrypath = root / entryname
                elif name.endswith(".pdf"):
                    entryname = f"{name[:-4]}.bib"
                    entrypath = root / entryname
                else:
                    continue

                if not entrypath.is_file():
                    console.print(
                        f":red_circle: [red]Found file without associated entry[/]: {filepath}"
                    )

                    error_count += 1

                    if fix:
                        console.print(
                            "  :arrow_forward: Removing file...",
                            end="",
                        )
                        filepath.unlink()
                        console.print(" [green]Done[/]")

                continue

            entry_count += 1

            # check that bib file is valid
            try:
                bib_library: Library = file_to_bib(filepath)
            except Exception as e:
                console.print(
                    f":red_circle: [red]Error parsing BibTeX file[/]: {filepath}"
                )
                console.print(f"  :down-right_arrow: {e}")
                error_count += 1
                continue

            if len(bib_library.entries) > 1:
                console.print(
                    f":red_circle: [red]Found file that contains multiple BibTeX entries[/]: {filepath}"
                )
                error_count += 1
                continue

            console.print(f"{filepath}: [green]No warnings raised[/]")

            # check if entry has a note
            notepath = root / f".{name[:-4]}.txt"
            if notepath.is_file():
                console.print(
                    f"  :arrow_forward: [yellow]Note found[/]: {notepath}"
                )
            else:
                console.print("  :red_circle: [red]No note found[/]")
                error_count += 1

            # check if entry has a PDF
            pdfpath = root / f"{name[:-4]}.pdf"
            if pdfpath.is_file():
                console.print(
                    f"  :arrow_forward: [yellow]PDF found[/]: {pdfpath}"
                )
            else:
                console.print("  :red_circle: [red]No PDF found[/]")
                error_count += 1

    console.print(
        f"\nChecked [green]{entry_count}[/] entries and a total of [red]{error_count}[/] errors were found"
    )
