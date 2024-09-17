import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
SCIHUB_URLS_LINK = "https://sci-hub.41610.org/"


# SciHub HTML parsing taken mostly from https://github.com/ferru97/PyPaperBot
def get_scihub_urls() -> list[str] | None:
    """
    Get a list of available Sci-Hub URLs

    :return: List of Sci-Hub URLs
    :rtype: list[str]
    """
    r = requests.get(SCIHUB_URLS_LINK, headers=HEADERS)
    if r.status_code == 200:
        response_text = r.text
    else:
        return None

    soup = BeautifulSoup(response_text, "html.parser")

    links = []
    for ul in soup.findAll("ul"):
        for a in ul.findAll("a"):
            link = a.get("href")
            if link.startswith("https://sci-hub.") or link.startswith(
                "http://sci-hub."
            ):
                links.append(link)

    return links


def get_scihub_contents(link: str) -> bytes | None:
    """
    Get the contents of the Sci-Hub link

    :param link: Sci-Hub link
    :type link: str
    :return: PDF file
    :rtype: bytes | None
    """
    r = requests.get(link, headers=HEADERS)
    if r.status_code == 200:
        return r.content
    return None


def extract_pdf_link_from_html(html: bytes) -> bytes | None:
    """
    Extract the PDF link from the HTML of the Sci-Hub page

    :param html: HTML content
    :type html: str
    :return: PDF file
    :rtype: bytes | None
    """
    soup = BeautifulSoup(html, "html.parser")

    iframe = soup.find(id="pdf")
    plugin = soup.find(id="plugin")
    result = None

    if iframe is not None:
        result = iframe.get("src")

    if plugin is not None and result is None:
        result = plugin.get("src")

    if result is not None and result[0] != "h":
        result = "https:" + result

    return result
