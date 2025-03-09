from urllib.parse import urlparse


def extract_source(url: str) -> str:
    "Extracts the source name from the URL."
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    source = domain.split('.')[0]
    return source.capitalize()
