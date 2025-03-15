import os
import json
import requests

COOKIE_JSON_FILE = "falabella_cookies.json"


def load_cookies_from_json(scraper, json_file=COOKIE_JSON_FILE):
    """
    Loads cookies from a JSON file and updates the scraper's cookie jar.

    The JSON file should be a list of dictionaries where each dictionary contains
    at least 'name', 'value', 'domain', and 'path' keys.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, json_file)

    with open(json_path, "r") as f:
        cookies_list = json.load(f)
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies_list:
        jar.set(cookie["name"], cookie["value"],
                domain=cookie["domain"], path=cookie.get("path", "/"))
    scraper.cookies.update(jar)
