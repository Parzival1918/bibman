from shutil import which
from pathlib import Path
from bibtexparser.bibdatabase import BibDatabase
from enum import StrEnum

def in_path(prog: str) -> bool:
    return which(prog) is not None


class QueryFields(StrEnum):
    TITLE = "title"
    ABSTRACT = "abstract"
    ENTRY = "ENTRYTYPE"
    AUTHOR = "author"


class Entry:
    path: Path
    contents: BibDatabase

    def __init__(self, path: Path, contents: BibDatabase):
        self.path = path

        if len(contents.entries) == 0:
            raise RuntimeError
        elif len(contents.entries) > 1:
            raise RuntimeError

        self.contents = contents


    def check_field_exists(self, field: str)-> bool:
        return field in self.contents.entries[0]


    def filter(self, query: str, field: QueryFields) -> bool:
        contents = self.contents.entries[0] 
        match field:
            case QueryFields.TITLE:
                if query:
                    return self.check_field_exists(QueryFields.TITLE.value) and query in contents[QueryFields.TITLE.value]
                else:
                    return True
            case QueryFields.ENTRY:
                if query:
                    return self.check_field_exists(QueryFields.ENTRY.value) and contents[QueryFields.ENTRY.value] in query 
                else:
                    return True
            case QueryFields.ABSTRACT:
                if query:
                    return self.check_field_exists(QueryFields.ABSTRACT.value) and query in contents[QueryFields.ABSTRACT.value]
                else:
                    return True
            case QueryFields.AUTHOR:
                if query:
                    return self.check_field_exists(QueryFields.AUTHOR.value) and query in contents[QueryFields.AUTHOR.value]
                else:
                    return True
            case _:
                raise RuntimeError


    def apply_filters(self, filters: dict) -> bool: # { field: query }
        for field, query in filters.items():
            if not self.filter(query, QueryFields[field]):
                return False

        return True


    def format_string(self, format: str) -> str:
        contents = self.contents.entries[0]

        formatted_string = format.replace("{path}", str(self.path)) # path
        if self.check_field_exists("title"): # title
            formatted_string = formatted_string.replace("{title}", contents["title"])
        else:
            formatted_string = formatted_string.replace("{title}", "ENTRY HAS NO TITLE")
        if self.check_field_exists("author"): # author
            formatted_string = formatted_string.replace("{author}", contents["author"])
        else:
            formatted_string = formatted_string.replace("{author}", "ENTRY HAS NO AUTHOR")

        return formatted_string