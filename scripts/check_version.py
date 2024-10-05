from pathlib import Path
import sys

PY_VERSION_FILE = (
    Path(__file__).parent.parent / "src" / "bibmancli" / "version.py"
)
PYPROJECT_TOML_FILE = Path(__file__).parent.parent / "pyproject.toml"
FLAKE_FILE = Path(__file__).parent.parent / "flake.nix"
CHANGELOG_FILE = Path(__file__).parent.parent / "CHANGELOG.md"
DOCS_CHANGELOG_FILE = Path(__file__).parent.parent / "docs" / "changelog.md"


def find_version(file: Path, version: str) -> int:
    """
    Check how many times 'file' has 'version' string

    :param file: pathlib.Path of file to check
    :type file: pathlib.Path
    :param version: version as a string
    :type version: str
    :return: Number of occurrences of 'version'
    :rtype: int
    """
    appearances = 0
    with open(file, mode="r") as f:
        while line := f.readline():
            if version in line:
                appearances += 1

    return appearances


version_to_compare = "NONE"
with open(CHANGELOG_FILE, mode="r") as f:
    while line := f.readline():
        if line.startswith("##"):
            version_to_compare = line[4:].strip()
            break


if version_to_compare == "NONE":
    print(f"Version not found in file '{CHANGELOG_FILE}'")
    sys.exit(1)

print(f"Checking for version '{version_to_compare}' in files")

files = [
    PY_VERSION_FILE,
    PYPROJECT_TOML_FILE,
    FLAKE_FILE,
    CHANGELOG_FILE,
    DOCS_CHANGELOG_FILE,
]

counts = [
    1,
    2,
    1,
    2,
    1,
]

err_count = 0
for file, count in zip(files, counts):
    if (appearances := find_version(file, version_to_compare)) == 0:
        print(f"File '{str(file)}' does not contain updated version number")
        err_count += 1
    elif appearances != count:
        print(
            f"File '{str(file)}' expected to have {count} but found {appearances}"
        )
        err_count += 1

if err_count > 0:
    sys.exit(1)
