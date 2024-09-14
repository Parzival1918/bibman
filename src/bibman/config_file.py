from pathlib import Path
from tomllib import load as load_toml
from tomllib import TOMLDecodeError


"""
This module contains functions for finding the library location.

The library is defined by a .bibman.toml file in the library parent directory.
File format:
    [library]
    location = "name_of_library_directory"
"""


def find_library() -> Path | None:
    """
    Find the library location by checking the current directory and all parent directories for a .bibman.toml file

    :return: Path to the library, or None if not found
    :rtype: Path | None
    """
    current_dir = Path.cwd()
    while current_dir != Path("/"):
        toml_file = current_dir / ".bibman.toml"
        if toml_file.exists():
            try:
                with open(toml_file, "rb") as f:
                    toml_data = load_toml(f)
            except TOMLDecodeError as e:
                raise e

            if "library" in toml_data and "location" in toml_data["library"]:
                library_path = current_dir / toml_data["library"]["location"]
                if library_path.exists():
                    return library_path
                return None
        current_dir = current_dir.parent

    return None


def get_library(path: Path) -> Path | None:
    """
    Get the library path from a given path

    :param path: Path to the .bibman.toml file directory
    :type path: Path
    :return: Path to the library
    :rtype: Path | None
    """
    toml_file = path / ".bibman.toml"
    if toml_file.exists():
        try:
            with open(toml_file, "rb") as f:
                toml_data = load_toml(f)
        except TOMLDecodeError as e:
            raise e

        if "library" in toml_data and "location" in toml_data["library"]:
            library_path = path / toml_data["library"]["location"]
            if library_path.exists():
                return library_path
            return None

    return None


def create_toml_contents(library_name: str) -> str:
    """
    Create the contents of a .bibman.toml file

    :param library_name: Name of the library directory
    :type library_name: str
    :return: Contents of the .bibman.toml file
    :rtype: str
    """
    return f'[library]\nlocation = "{library_name}"\n'
