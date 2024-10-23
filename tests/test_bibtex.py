from bibmancli import bibtex
import tempfile
import pathlib
import pytest
from entries import BIB_STR, MULTIPLE_BIB_STR, ERROR_BIB_STR


def test_string_to_bib():
    bib_library = bibtex.string_to_bib(BIB_STR)

    assert len(bib_library.entries) == 1

    beran_entry = bib_library.entries_dict["beran_frontiers_2023"]

    assert beran_entry.get("year").value == "2023"


def test_file_to_bib():
    with tempfile.TemporaryDirectory() as dir:
        bib_file = pathlib.Path(dir + "/entry.bib")
        bib_file.write_text(BIB_STR)

        bib_library = bibtex.file_to_bib(bib_file)

    assert len(bib_library.entries) == 1

    beran_entry = bib_library.entries_dict["beran_frontiers_2023"]

    assert beran_entry.get("year").value == "2023"

    with tempfile.TemporaryDirectory() as dir:
        bib_file = pathlib.Path(dir + "/entry.bib")
        bib_file.write_text(ERROR_BIB_STR)

        with pytest.raises(
            ValueError, match="No entries found in the BibTeX file"
        ):
            bib_library = bibtex.file_to_bib(bib_file)

    with tempfile.TemporaryDirectory() as dir:
        bib_file = pathlib.Path(dir + "/entry.bib")
        bib_file.write_text(MULTIPLE_BIB_STR)

        with pytest.raises(
            ValueError, match="Multiple entries found in the BibTeX file"
        ):
            bib_library = bibtex.file_to_bib(bib_file)


def test_file_to_library():
    pass


def test_bib_to_string():
    pass
