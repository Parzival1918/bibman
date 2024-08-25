from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from pathlib import Path


# From https://github.com/timothygebhard/doi2bibtex/blob/main/doi2bibtex/bibtex.py
def string_to_dict(contents: str) -> dict:
    parser = BibTexParser(ignore_nonstandard_types=False)
    bibtex_dict = dict(parser.parse(contents).entries[0])

    return bibtex_dict

def string_to_bib(contents: str) -> BibDatabase:
    parser = BibTexParser(ignore_nonstandard_types=False)

    try:
        bib = parser.parse(contents)
    except Exception as e:
        raise e

    return bib


def file_to_bib(file: Path) -> BibDatabase:
    with open(file, "r") as f:
        contents = f.read()

    bib = string_to_bib(contents)

    return bib


# From https://github.com/timothygebhard/doi2bibtex/blob/main/doi2bibtex/bibtex.py
def dict_to_bibtex_string(bibtex_dict: dict) -> str:
    """
    Convert a BibTeX dictionary to a string.
    """

    # Convert the BibTeX dict to a BibDatabase object
    database = BibDatabase()
    database.entries = [bibtex_dict]

    # Set up a BibTeX writer
    writer = BibTexWriter()
    writer.align_values = 13
    writer.add_trailing_commas = True
    writer.indent = '    '

    # Convert the BibDatabase object to a string
    bibtex_string = str(writer.write(database)).strip()

    return bibtex_string


def bib_to_string(bib: BibDatabase) -> str:
    # Set up a BibTeX writer
    writer = BibTexWriter()
    writer.align_values = 13
    writer.add_trailing_commas = True
    writer.indent = '    '

    try:
        bibtex_string = str(writer.write(bib)).strip()
    except Exception as e:
        raise e

    return bibtex_string