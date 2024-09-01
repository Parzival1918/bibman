# from bibtexparser.bibdatabase import BibDatabase
# from bibtexparser.bparser import BibTexParser
# from bibtexparser.bwriter import BibTexWriter
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
    # parser = BibTexParser(ignore_nonstandard_types=False)

    try:
        bib_library = parse_string(contents)
    except Exception as e:
        raise e

    return bib_library


def file_to_bib(file: Path) -> Library:
    # with open(file, "r") as f:
    #     contents = f.read()

    # bib = string_to_bib(contents)

    bib_library = parse_file(file)
    if len(bib_library.entries) == 0:
        raise ValueError("No entries found in the BibTeX file")
    elif len(bib_library.entries) > 1:
        raise ValueError("Multiple entries found in the BibTeX file")

    return bib_library


def bib_to_string(bib_library: Library) -> str:
    # Set up a BibTeX writer
    # writer = BibTexWriter()
    # writer.align_values = 13
    # writer.add_trailing_commas = True
    # writer.indent = '    '

    # try:
    #     bibtex_string = str(writer.write(bib)).strip()
    # except Exception as e:
    #     raise e
    
    format = BibtexFormat()
    format.value_column = 13
    format.trailing_comma = True
    format.indent = '    '
    
    bib_str = write_string(bib_library, bibtex_format=format)

    return bib_str