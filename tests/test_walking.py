from bibmancli.utils import iterate_files
from pathlib import Path


def test_iterate_files():
    path = Path(__file__).parent / "files" / "library"
    files = iterate_files(path)
    assert len(list(files)) == 4
