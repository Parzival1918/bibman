import requests
from urllib.parse import quote_plus
from bibman.bibtex import string_to_dict


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


def resolve_identifier(identifier: str, timeout: float) -> dict:
    # send the request
    try:
        r = send_request(identifier, timeout)
    except Exception as e:
        raise e

    # parse response into dict
    bibtex = string_to_dict(r.text)

    return bibtex
