from bibmancli import utils, bibtex
import tempfile
import pathlib
from entries import BIB_STR


def test_Entry_class():
    with tempfile.TemporaryDirectory() as dir:
        bib_file = pathlib.Path(dir + "/normal.bib")
        bib_file.write_text(BIB_STR)
        library = bibtex.file_to_bib(bib_file)
        entry = library.entries[0]

        entry_class = utils.Entry(bib_file, entry)

        assert entry_class.check_field_exists("title")
        assert entry_class.check_field_exists("year")
        assert entry_class.check_field_exists("doi")
        assert not entry_class.check_field_exists("isbn")
        assert not entry_class.check_field_exists("abstract")

        assert not (entry_class.filter("Contents", utils.QueryFields.ABSTRACT))
        assert entry_class.filter("Frontiers", utils.QueryFields.TITLE)
        assert entry_class.filter(
            "Beran, Gregory J. O.", utils.QueryFields.AUTHOR
        )
        assert entry_class.filter("article", utils.QueryFields.ENTRY)


def test_filtering_entries():
    pass
