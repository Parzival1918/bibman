from bibtexparser.library import Library
from bibtexparser.model import Entry as BibEntry
from bibtexparser.entrypoint import parse_string, parse_file, write_string
from bibtexparser.writer import BibtexFormat
from pathlib import Path


# From https://github.com/timothygebhard/doi2bibtex/blob/main/doi2bibtex/bibtex.py
# def string_to_dict(contents: str) -> dict:
#     # parser = BibTexParser(ignore_nonstandard_types=False)
#     # bibtex_dict = dict(parser.parse(contents).entries[0])

#     bib_library: Library = parse_string(contents)
#     bibtex_dict = bib_library.entries_dict

#     return bibtex_dict


# # From https://github.com/timothygebhard/doi2bibtex/blob/main/doi2bibtex/bibtex.py
# def dict_to_bibtex_string(bibtex_dict: dict) -> str:
#     """
#     Convert a BibTeX dictionary to a string.
#     """

#     # Convert the BibTeX dict to a BibDatabase object
#     database = BibDatabase()
#     database.entries = [bibtex_dict]

#     # Set up a BibTeX writer
#     writer = BibTexWriter()
#     writer.align_values = 13
#     writer.add_trailing_commas = True
#     writer.indent = '    '

#     # Convert the BibDatabase object to a string
#     bibtex_string = str(writer.write(database)).strip()

#     return bibtex_string


def string_to_bib(contents: str) -> Library:
    """
    Parse a string into a BibTeX library.

    :param contents: String to parse
    :type contents: str
    :return: BibTeX library
    :rtype: bibtexparser.library.Library
    """
    try:
        bib_library = parse_string(contents)
    except Exception as e:
        raise e

    return bib_library


def file_to_bib(file: Path) -> Library:
    """
    Parse a file into a BibTeX library.

    :param file: Path to the file
    :type file: pathlib.Path
    :return: BibTeX library
    :rtype: bibtexparser.library.Library
    """
    try:
        bib_library = parse_file(file)
    except Exception as e:
        raise e

    if len(bib_library.entries) == 0:
        raise ValueError("No entries found in the BibTeX file")
    elif len(bib_library.entries) > 1:
        raise ValueError("Multiple entries found in the BibTeX file")

    return bib_library


def bib_to_string(bib_library: Library | BibEntry) -> str:
    """
    Convert a BibTeX library or entry to a string.

    :param bib_library: BibTeX library or entry
    :type bib_library: bibtexparser.library.Library | bibtexparser.model.Entry
    :return: BibTeX string
    :rtype: str
    """
    if isinstance(bib_library, BibEntry):
        entry = bib_library
        bib_library = Library()
        bib_library.add(entry)

    format = BibtexFormat()
    format.value_column = 13
    format.trailing_comma = True
    format.indent = "    "

    bib_str = write_string(bib_library, bibtex_format=format)

    return bib_str


def file_to_library(file: Path) -> Library:
    """
    Parse a file into a BibTeX library.

    :param file: Path to the file
    :type file: pathlib.Path
    :return: BibTeX library
    :rtype: bibtexparser.library.Library
    """
    bib_library = parse_file(file)

    return bib_library
