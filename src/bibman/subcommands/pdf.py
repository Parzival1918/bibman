import typer
from typing_extensions import Annotated
from rich.console import Console
from typing import Optional
from pathlib import Path
import requests
from rich.progress import Progress, SpinnerColumn, TextColumn
from bibman.pdf_utils import (
    get_scihub_urls,
    get_scihub_contents,
    extract_pdf_link_from_html,
)
from bibman.config_file import find_library, get_library
from bibman.utils import iterate_files


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

app = typer.Typer(
    no_args_is_help=True,
    help="""
    Add or download PDF files of library entries.
    """,
)

console = Console()
err_console = Console(stderr=True)


@app.command()
def download(
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
    Download PDF file of all library entries.
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
            description="Retrieving Sci-Hub URLs...",
        )
        scihub_urls = get_scihub_urls()

    if scihub_urls is None:
        err_console.print("[bold red]ERROR[/] Unable to retrieve Sci-Hub URLs")
        raise typer.Exit(1)

    console.print("[green]Sci-Hub URLs retrieved[/]")

    # iterate over the entries and download the PDFs
    download_count = 0
    entry_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn(text_format="[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        for file in iterate_files(location):
            entry_count += 1

            filename = file.path.stem + ".pdf"
            pdf_path = file.path.parent / filename

            if pdf_path.exists():
                console.print(
                    f"[bold yellow]WARNING[/] PDF already exists for entry '{file.path.relative_to(location)}'"
                )
                continue

            task = progress.add_task(
                description=f"Checking bib contents of '{file.path.relative_to(location)}'...",
            )

            # Check if file has DOI
            if file.contents.fields_dict.get("doi") is None:
                progress.remove_task(task)
                console.print(
                    f"[bold yellow]WARNING[/] No DOI found for {file.path.relative_to(location)}"
                )
                continue

            # try downloading the PDF using the Sci-Hub URLs
            progress.update(
                task,
                description=f"Searching PDF for '{file.contents.fields_dict['doi'].value}'...",
            )
            for url in scihub_urls:
                # download the PDF
                progress.update(
                    task,
                    description=f"Searching PDF for '{file.contents.fields_dict['doi'].value}' at '{url}'...",
                )
                link = f"{url}/{file.contents.fields_dict['doi']}"

                sci_hub_contents = get_scihub_contents(link)
                if sci_hub_contents is None:
                    continue

                pdf_link = extract_pdf_link_from_html(sci_hub_contents)
                if pdf_link is None:
                    continue

                progress.update(
                    task,
                    description=f"PDF link found for '{file.contents.fields_dict['doi'].value}' attempting to download...",
                )

                # attempt to download the PDF
                r = requests.get(pdf_link, headers=HEADERS)
                if r.status_code == 200:
                    if pdf_path.exists():
                        console.print(
                            f"[bold yellow]WARNING[/] PDF already exists for entry '{file.path.relative_to(location)}', overwriting..."
                        )

                    with open(pdf_path, "wb") as f:
                        f.write(r.content)
                    console.print(
                        f"[green]PDF downloaded[/] to '{pdf_path}' for entry '{file.path.relative_to(location)}'"
                    )
                    download_count += 1
                    progress.remove_task(task)
                    break
                else:
                    console.print(
                        f"[bold red]ERROR[/] Unable to download PDF from '{pdf_link}' for entry '{file.contents.fields_dict['doi']}'"
                    )

                progress.remove_task(task)
            else:
                console.print(
                    f"[bold red]ERROR[/] No PDF found for '{file.contents.fields_dict['doi']}'"
                )

    console.print(
        f"Downloaded [green]{download_count}[/] PDFs out of [yellow]{entry_count}[/] entries"
    )


@app.command()
def add(
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
    Add PDF file of one entry fronm a local file.
    """
    pass
