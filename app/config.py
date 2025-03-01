# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.environ.get('OPENAI_KEY')
if not OPENAI_KEY:
    raise ValueError("OPENAI_KEY environment variable is not set.")


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

BROWSER = {
    'browser': 'chrome',
    'platform': 'windows',
                'mobile': False
}

service_name = 'scraper_py'
