from shutil import which
from pathlib import Path
from bibtexparser.bibdatabase import BibDatabase
from enum import StrEnum
from collections.abc import Iterable
from pylatexenc.latex2text import LatexNodes2Text
from bibman.bibtex import file_to_bib

def in_path(prog: str) -> bool:
    return which(prog) is not None


class QueryFields(StrEnum):
    TITLE = "title"
    ABSTRACT = "abstract"
    ENTRY = "ENTRYTYPE"
    AUTHOR = "author"


class Entry:
    path: Path
    contents: BibDatabase

    def __init__(self, path: Path, contents: BibDatabase):
        self.path = path

        if len(contents.entries) == 0:
            raise RuntimeError
        elif len(contents.entries) > 1:
            raise RuntimeError

        self.contents = contents


    def check_field_exists(self, field: str)-> bool:
        return field in self.contents.entries[0]


    def filter(self, query: str, field: QueryFields) -> bool:
        contents = self.contents.entries[0] 
        match field:
            case QueryFields.TITLE:
                if query:
                    return self.check_field_exists(QueryFields.TITLE.value) and query in contents[QueryFields.TITLE.value]
                else:
                    return True
            case QueryFields.ENTRY:
                if query:
                    return self.check_field_exists(QueryFields.ENTRY.value) and contents[QueryFields.ENTRY.value] in query 
                else:
                    return True
            case QueryFields.ABSTRACT:
                if query:
                    return self.check_field_exists(QueryFields.ABSTRACT.value) and query in contents[QueryFields.ABSTRACT.value]
                else:
                    return True
            case QueryFields.AUTHOR:
                if query:
                    return self.check_field_exists(QueryFields.AUTHOR.value) and query in contents[QueryFields.AUTHOR.value]
                else:
                    return True
            case _:
                raise RuntimeError


    def apply_filters(self, filters: dict) -> bool: # { field: query }
        for field, query in filters.items():
            if not self.filter(query, QueryFields[field]):
                return False

        return True


    def format_string(self, format: str) -> str:
        contents = self.contents.entries[0]

        formatted_string = format.replace("{path}", str(self.path)) # path
        if self.check_field_exists("title"): # title
            formatted_string = formatted_string.replace("{title}", contents["title"])
        else:
            formatted_string = formatted_string.replace("{title}", "ENTRY HAS NO TITLE")
        if self.check_field_exists("author"): # author
            formatted_string = formatted_string.replace("{author}", contents["author"])
        else:
            formatted_string = formatted_string.replace("{author}", "ENTRY HAS NO AUTHOR")

        return formatted_string
    

def iterate_files(path: Path, filetype: str = ".bib") -> Iterable[Entry]:
    for root, _, files in path.walk():
        for name in files:
            if name.endswith(filetype): # only count bib files
                file = root / name

                # read the file contents
                bib = file_to_bib(file)

                yield Entry(file, bib)


def create_html(location: Path) -> str:
    html = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>BIBMAN</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    </head>
    <body>
        <div class="container-md align-items-center justify-content-center px-5">
            <div class="input-group my-3">
                <input type="text" class="form-control" placeholder="Search" aria-label="Search" aria-describedby="button-search" id="input-search">
                <button class="btn btn-outline-primary" type="button" id="button-search" onclick="SearchClick()">Search</button>
                <button class="btn btn-outline-secondary" type="button" id="button-clear" onclick="ClearClick()">Clear</button>
            </div>
    """

    for entry in iterate_files(location):
        note_path = entry.path.parent / ("." + entry.path.name.replace(".bib", ".txt"))
        html += f"""
            <div class="card my-4 bib-entry">
                <div class="card-header text-body-secondary fs-6">
                    Location: {str(entry.path.relative_to(location).as_posix())}
                </div>
                <div class="card-body">
                    <h5 class="card-title">{LatexNodes2Text().latex_to_text(entry.contents.entries[0]["title"])}</h5>
                    <h6 class="card-subtitle mb-2 text-body-secondary">{entry.contents.entries[0]["author"]}</h6>
                </div>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">
                        {note_path.read_text()}
                    </li>
                </ul>
            </div>
        """

    html += """
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script>
            function SearchClick() {
                let search_string = document.getElementById("input-search").value;
                let bibEntries = document.getElementsByClassName("bib-entry");

                for (let i = 0; i < bibEntries.length; i++) {
                    let entry = bibEntries[i];
                    let title = entry.getElementsByClassName("card-title")[0].innerText;
                    let author = entry.getElementsByClassName("card-subtitle")[0].innerText;
                    let note = entry.getElementsByClassName("list-group-item")[0].innerText;

                    if (title.includes(search_string) || author.includes(search_string) || note.includes(search_string)) {
                        entry.style.display = "block";
                    } else {
                        entry.style.display = "none";
                    }
                }
            };

            function ClearClick() {
                let bibEntries = document.getElementsByClassName("bib-entry");

                for (let i = 0; i < bibEntries.length; i++) {
                    let entry = bibEntries[i];
                    entry.style.display = "block";
                }

                document.getElementById("input-search").value = "";
            };

            // Search on Enter key press
            document.getElementById("input-search").addEventListener("keyup", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    SearchClick();
                }

                if (event.key === "Escape") {
                    event.preventDefault();
                    ClearClick();
                }
            });
        </script>
    </body>
    </html>
    """

    return html