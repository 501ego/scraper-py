# config.py
import os
from dotenv import load_dotenv

load_dotenv()


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none"
}


BROWSER = {
    'browser': 'chrome',
    'platform': 'windows',
                'mobile': False
}

service_name = 'scraper_py'

OPENAI_KEY = os.environ.get('OPENAI_KEY')
if not OPENAI_KEY:
    raise ValueError("OPENAI_KEY environment variable is not set.")
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")
MONGO_DB = os.environ.get("MONGO_DB")
if not MONGO_DB:
    raise ValueError("MONGO_DB environment variable is not set.")
MONGO_COLLECTION1 = os.environ.get("MONGO_COLLECTION1")
if not MONGO_COLLECTION1:
    raise ValueError("MONGO_COLLECTION environment variable is not set.")
MONGO_COLLECTION2 = os.environ.get("MONGO_COLLECTION2")
if not MONGO_COLLECTION2:
    raise ValueError("MONGO_COLLECTION2 environment variable is not set.")
CLIENT_ID = os.environ.get("CLIENT_ID")
if not CLIENT_ID:
    raise ValueError("CLIENT_ID environment variable is not set.")
GUILD_ID = os.environ.get("GUILD_ID")
if not GUILD_ID:
    raise ValueError("GUILD_ID environment variable is not set.")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID environment variable is not set.")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("DISCORDJS_BOT_TOKEN environment variable is not set.")

# Labels for logging each field per source.
PARIS_LABELS = {
    "name": "Product Name",
    "price1": "Cencosud Price",
    "price2": "Internet Price",
    "price3": "Normal Price",
    "timestamp": "Timestamp"
}

FALABELLA_LABELS = {
    "name": "Product Name",
    "price1": "CMR Price",
    "price2": "Internet Price",
    "price3": "Normal Price",
    "timestamp": "Timestamp"
}
PRICE_FIELDS = ["price1", "price2", "price3"]
SOURCES = ["Paris", "Falabella"]
