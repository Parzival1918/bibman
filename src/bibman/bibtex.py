from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter


def string_to_dict(contents: str) -> dict:
    parser = BibTexParser(ignore_nonstandard_types=False)
    bibtex_dict = dict(parser.parse(contents).entries[0])

    return bibtex_dict


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
