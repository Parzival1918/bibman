from shutil import which
from pathlib import Path
import json
from bibtexparser.model import Entry as BibEntry
from enum import StrEnum
from collections.abc import Iterable
from pylatexenc.latex2text import LatexNodes2Text
from bibmancli.bibtex import file_to_bib


def in_path(prog: str) -> bool:
    """
    Check if a program is in the PATH
    """
    return which(prog) is not None


class QueryFields(StrEnum):
    """
    Enum for the fields that can be queried
    """

    TITLE = "title"
    ABSTRACT = "abstract"
    ENTRY = "ENTRYTYPE"
    AUTHOR = "author"


class Entry:
    """
    Class to represent a single entry in the library

    :param path: Path to the file
    :type path: Path
    :param contents: Contents of the entry, as a BibEntry object
    :type contents: BibEntry
    """

    path: Path
    contents: BibEntry

    def __init__(self, path: Path, contents: BibEntry):
        """
        Initialize the Entry object

        :param path: Path to the file
        :type path: Path
        :param contents: Contents of the entry, as a BibEntry object
        :type contents: BibEntry
        """
        self.path = path

        self.contents = contents

    def check_field_exists(self, field: str) -> bool:
        """
        Check if a field exists in the entry

        :param field: Field to check
        :type field: str
        :return: True if the field exists, False otherwise
        :rtype: bool
        """
        return field in self.contents.fields_dict

    def filter(self, query: str, field: QueryFields) -> bool:
        """
        Check if the entry passes the filter

        :param query: Query string
        :type query: str
        :param field: Field to query
        :type field: QueryFields
        :return: True if the entry passes the filter, False otherwise
        :rtype: bool
        """
        contents = self.contents.fields_dict
        match field:
            case QueryFields.TITLE:
                if query:
                    return (
                        self.check_field_exists(QueryFields.TITLE.value)
                        and query in contents[QueryFields.TITLE.value].value
                    )
                else:
                    return True
            case QueryFields.ENTRY:
                if query:
                    return (
                        self.check_field_exists(QueryFields.ENTRY.value)
                        and contents[QueryFields.ENTRY.value].value in query
                    )
                else:
                    return True
            case QueryFields.ABSTRACT:
                if query:
                    return (
                        self.check_field_exists(QueryFields.ABSTRACT.value)
                        and query in contents[QueryFields.ABSTRACT.value].value
                    )
                else:
                    return True
            case QueryFields.AUTHOR:
                if query:
                    return (
                        self.check_field_exists(QueryFields.AUTHOR.value)
                        and query in contents[QueryFields.AUTHOR.value].value
                    )
                else:
                    return True
            case _:
                raise RuntimeError

    def apply_filters(self, filters: dict) -> bool:  # { field: query }
        """
        Apply filters to the entry. Pass only if all filters pass

        :param filters: Filters to apply. Dictionary of **field: query** pairs
        :type filters: dict
        :return: True if the entry passes all filters, False otherwise
        :rtype: bool
        """
        for field, query in filters.items():
            if not self.filter(query, QueryFields[field]):
                return False

        return True

    def format_string(self, format: str) -> str:
        """
        Format the entry as a string using a format string.

        For example, the format string "{title} by {author}" will be formatted as "Title by Author"

        Available fields are: path, title, author, year, month, entry_name, entry_type

        :param format: Format string
        :type format: str
        :return: Formatted string
        :rtype: str
        """
        contents = self.contents.fields_dict

        formatted_string = format.replace("{path}", str(self.path))  # path
        if self.check_field_exists("title"):  # title
            formatted_string = formatted_string.replace(
                "{title}",
                LatexNodes2Text().latex_to_text(contents["title"].value),
            )
        else:
            formatted_string = formatted_string.replace(
                "{title}", "ENTRY HAS NO TITLE"
            )
        if self.check_field_exists("author"):  # author
            formatted_string = formatted_string.replace(
                "{author}",
                LatexNodes2Text().latex_to_text(contents["author"].value),
            )
        else:
            formatted_string = formatted_string.replace(
                "{author}", "ENTRY HAS NO AUTHOR"
            )
        if self.check_field_exists("year"):  # year
            formatted_string = formatted_string.replace(
                "{year}",
                LatexNodes2Text().latex_to_text(contents["year"].value),
            )
        else:
            formatted_string = formatted_string.replace(
                "{year}", "ENTRY HAS NO YEAR"
            )
        if self.check_field_exists("month"):
            formatted_string = formatted_string.replace(
                "{month}",
                LatexNodes2Text().latex_to_text(contents["month"].value),
            )
        else:
            formatted_string = formatted_string.replace(
                "{month}", "ENTRY HAS NO MONTH"
            )

        formatted_string = formatted_string.replace(
            "{entry_type}", self.contents.entry_type
        )

        return formatted_string


def iterate_files(path: Path, filetype: str = ".bib") -> Iterable[Entry]:
    """
    Iterate over all files in a directory and its subdirectories,
    yielding the entries in each file as Entry objects

    :param path: Path to the directory
    :type path: Path
    :param filetype: Filetype to search for
    :type filetype: str
    :return: Generator yielding Entry objects
    :rtype: Iterable[Entry]
    """
    for root, _, files in path.walk():
        for name in files:
            if name.endswith(filetype):  # only count bib files
                file = root / name

                # read the file contents
                bib = file_to_bib(file)

                yield Entry(file, bib.entries[0])


def entries_as_json_string(
    entries: Iterable[Entry], library_location: Path
) -> str:
    """
    Convert entries to a JSON string. The library location is used to generate relative paths.

    :param entries: Entries to convert
    :type entries: Iterable[Entry]
    :param library_location: Location of the library
    :type library_location: Path
    :return: JSON string
    :rtype: str
    """
    json_entries = []
    for entry in entries:
        entry_dict = {field.key: field.value for field in entry.contents.fields}
        for key in entry_dict:
            entry_dict[key] = LatexNodes2Text().latex_to_text(entry_dict[key])

        note_path = entry.path.parent / ("." + entry.path.stem + ".txt")
        if note_path.exists():
            entry_dict["note"] = note_path.read_text().strip()
        else:
            entry_dict["note"] = "No note available"

        entry_dict = {
            "path": entry.path.relative_to(library_location).as_posix(),
            "contents": entry_dict,
        }
        json_entries.append(entry_dict)

    return json.dumps(json_entries, indent=4, ensure_ascii=False)


def create_html(location: Path) -> str:
    """
    Create an HTML page to display the library entries

    :param location: Location of the library
    :type location: Path
    :return: HTML string
    :rtype: str
    """
    json_string = entries_as_json_string(iterate_files(location), location)

    html = (
        """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>BIBMAN</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    </head>
    <body>
        <div class="container-md align-items-center justify-content-center px-5" id="main-container">
            <div class="input-group my-3">
                <input type="text" class="form-control" placeholder="Search" aria-label="Search" aria-describedby="button-clear" id="input-search">
                <!-- 
                <button class="btn btn-outline-primary" type="button" id="button-search" onclick="SearchClick()">Search</button>
                -->
                <button class="btn btn-outline-secondary" type="button" id="button-settings" data-bs-toggle="modal" data-bs-target="#settingsModal">Config</button>
                <button class="btn btn-outline-secondary" type="button" id="button-clear" onclick="ClearClick()">Clear</button>
            </div>
            <div class="modal fade" id="entryModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5" id="exampleModalLabel">Entry contents</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="modal-body"></div>
                    </div>
                </div>
            </div>
            <div class="modal fade" id="settingsModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                    <div class="modal-header">
                        <h1 class="modal-title fs-5" id="exampleModalLabel">Settings</h1>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="input-group mb-3">
                            <span class="input-group-text" id="basic-addon1">Sci-Hub Link</span>
                            <input type="text" class="form-control" value="https://sci-hub.se/" aria-label="sci-hub" id="sci-hub-link">
                        </div>
                    </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/fuzzysort@3.0.2/fuzzysort.min.js"></script>
        <script>
            // Load entries from JSON string
            let entries = JSON.parse(`"""
        + json_string.replace("\\", "\\\\")
        + """`);

            function clickedEntry(i) {
                var modal = new bootstrap.Modal(document.getElementById('entryModal'));

                // show modal with entry contents
                let entry = entries[i];
                let modalBody = document.getElementById("modal-body");
                modalBody.innerText = "";
                for (let key in entry.contents) {
                    if (key === "note") {
                        continue;
                    }
                    // write the key in an h6 tag and the value in a p tag, show them side by side not in separate lines
                    let keyElement = document.createElement("p");
                    keyElement.className = "my-2 fw-bold";
                    keyElement.innerText = key + ": ";
                    let valueElement = document.createElement("p");
                    valueElement.className = "m-2";
                    valueElement.innerText = entry.contents[key];
                    let div = document.createElement("div");
                    div.className = "d-flex justify-content-start";
                    div.appendChild(keyElement);
                    div.appendChild(valueElement);
                    modalBody.appendChild(div);
                }
                // add button to sci-hub the entry if it has a DOI
                if (entry.contents.doi) {
                    let div = document.createElement("div");
                    div.className = "d-grid col-6 mx-auto";
                    let button = document.createElement("button");
                    button.className = "btn btn-secondary";
                    button.innerText = "Open in Sci-Hub";

                    // get sci-hub link from settings
                    let sciHubLink = document.getElementById("sci-hub-link").value;
                    button.onclick = function() {
                        window.open(sciHubLink + entry.contents.doi, "_blank");
                    };
                    div.appendChild(button);
                    modalBody.appendChild(div);
                }
                
                modal.show();
            };

            // function to create HTML elements for each entry
            function createEntryHTML(entry, i) {
                let card = document.createElement("div");
                card.className = "card my-4 bib-entry";
                card.id = entry.html_id;
                let cardHeader = document.createElement("div");
                cardHeader.className = "card-header text-body-secondary fs-6";
                cardHeader.innerText = "Location: " + entry.path;
                let cardBody = document.createElement("div");
                cardBody.className = "card-body";
                let title = document.createElement("h5");
                title.className = "card-title";
                title.innerText = entry.contents.title;
                let author = document.createElement("h6");
                author.className = "card-subtitle mb-2 text-body-secondary";
                author.innerText = entry.contents.author;
                let listGroup = document.createElement("ul");
                listGroup.className = "list-group list-group-flush";
                let listItem = document.createElement("li");
                listItem.className = "list-group-item";
                listItem.innerText = entry.contents.note;
                let link = document.createElement("a");
                link.className = "stretched-link";
                link.setAttribute("href", "#");
                link.setAttribute("onclick", "clickedEntry(" + i + ")");

                cardBody.appendChild(title);
                cardBody.appendChild(author);
                card.appendChild(cardHeader);
                card.appendChild(cardBody);
                listGroup.appendChild(listItem);
                card.appendChild(listGroup);
                card.appendChild(link);

                return card;
            }

            // Create HTML elements for each entry
            let mainContainer = document.getElementById("main-container");
            for (let i = 0; i < entries.length; i++) {
                let entry = entries[i];
                entry["html_id"] = "PATH-" + entry.path;
                // console.log(entry);
                let entryHTML = createEntryHTML(entry, i);
                mainContainer.appendChild(entryHTML);
            }

            // Enable fuzzy search as you type in the search bar
            let bibEntries = document.getElementsByClassName("bib-entry");
            let searchInput = document.getElementById("input-search");
            function fuzzy() {
                // If the search bar is empty, show all entries
                let search_string = searchInput.value;

                // Fuzzy search on multiple keys
                let results = fuzzysort.go(search_string, entries, {keys: ["contents.title", "contents.author", "contents.note"], limit: 15, all: true});
                for (let i = 0; i < bibEntries.length; i++) {
                    bibEntries[i].style.display = "none";
                }
                for (let i = 0; i < results.length; i++) {
                    let result = results[i];
                    let entry = document.getElementById(result.obj.html_id);

                    entry.style.display = "block";
                }
            };

            searchInput.addEventListener("input", function () {
                fuzzy();
            });

            function ClearClick() {
                document.getElementById("input-search").value = "";
                fuzzy();
            };
        </script>
    </body>
    </html>
    """
    )

    return html
