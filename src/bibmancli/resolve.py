import requests
from urllib.parse import quote_plus
from bibmancli.bibtex import string_to_bib
from bibtexparser.library import Library
from habanero import cn


def send_request(identifier: str, timeout: float) -> requests.Response:
    """
    Send a request to the Wikipedia REST API to resolve an identifier.

    :param identifier: Identifier of the entry
    :type identifier: str
    :param timeout: Request timeout in seconds
    :type timeout: float
    :return: Response object
    :rtype: requests.Response
    """
    # format identifier
    identifier = quote_plus(identifier)

    req = f"https://en.wikipedia.org/api/rest_v1/data/citation/bibtex/{identifier}"
    r = requests.get(req, timeout=timeout, headers={"Accept-Language": "en"})

    if (error := r.status_code) != 200:
        raise RuntimeError(f"Error resolving identifier: {error}")

    return r


def send_request_habanero(identifier: str, timeout: float) -> str:
    """
    Send a request to the CrossRef API to resolve an identifier.

    Seems to be worse than the Wikipedia API, but it's here just in case.

    :param identifier: Identifier of the entry
    :type identifier: str
    :param timeout: Request timeout in seconds
    :type timeout: float
    :return: BibTeX string
    :rtype: str
    """
    try:
        bib_str = cn.content_negotiation(
            ids=identifier, format="bibtex", timeout=timeout
        )
    except Exception as e:
        raise RuntimeError(f"Error resolving identifier: {e}")

    return bib_str


def resolve_identifier(identifier: str, timeout: float) -> Library:
    """
    Resolve an identifier to a BibTeX entry.

    :param identifier: Identifier of the entry
    :type identifier: str
    :param timeout: Request timeout in seconds
    :type timeout: float
    :return: BibTeX entry
    :rtype: bibtexparser.library.Library
    """
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
