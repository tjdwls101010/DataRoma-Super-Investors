"""Internal HTTP request layer with rate limiting."""

import time

import requests

BASE_URL = "https://www.dataroma.com/m"

_last_request_time = 0.0
_MIN_INTERVAL = 1.5  # seconds between requests

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
})


def fetch(path: str, params: dict | None = None) -> str:
    """Fetch a page from DataRoma with rate limiting.

    Returns the HTML content as a string.
    """
    global _last_request_time

    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    url = f"{BASE_URL}/{path}"
    resp = _SESSION.get(url, params=params, timeout=30)
    _last_request_time = time.time()
    resp.raise_for_status()
    return resp.text
