import requests
from urllib.parse import quote_plus
from bibman.bibtex import string_to_bib
from bibtexparser.bibdatabase import BibDatabase


def send_request(identifier: str, timeout: float):
    # format identifier
    identifier = quote_plus(identifier)

    req = f"https://en.wikipedia.org/api/rest_v1/data/citation/bibtex/{identifier}"
    r = requests.get(
        req,
        timeout=timeout,
        headers={
            "Accept-Language": "en"
        }
    )

    if (error := r.status_code) != 200:
        raise RuntimeError(f"Error resolving identifier: {error}")

    return r


def resolve_identifier(identifier: str, timeout: float) -> BibDatabase:
    # send the request
    try:
        r = send_request(identifier, timeout)
    except Exception as e:
        raise e

    # parse response into dict
    try:
        bibtex = string_to_bib(r.text)
    except Exception as e:
        raise e
        
    return bibtex
