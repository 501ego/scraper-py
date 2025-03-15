# config.py
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.5845.141 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-CH-UA": '"Chromium";v="116", "Google Chrome";v="116", "Not:A-Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Origin": "https://www.falabella.com"
}


BROWSER = {
    'browser': 'chrome',
    'platform': 'windows',
                'mobile': False
}

service_name = 'scraper_py'


def get_secret_or_env(secret_name: str, env_name: str) -> str:
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    return os.environ.get(env_name)


PROJECT_PREFIX = "scraper_py_"

OPENAI_KEY = get_secret_or_env(f"{PROJECT_PREFIX}openai_key", "OPENAI_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_KEY environment variable or secret is not set.")

MONGO_URI = get_secret_or_env(f"{PROJECT_PREFIX}mongo_uri", "MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable or secret is not set.")

MONGO_DB = get_secret_or_env(f"{PROJECT_PREFIX}mongo_db", "MONGO_DB")
if not MONGO_DB:
    raise ValueError("MONGO_DB environment variable or secret is not set.")

MONGO_COLLECTION1 = get_secret_or_env(
    f"{PROJECT_PREFIX}mongo_collection1", "MONGO_COLLECTION1")
if not MONGO_COLLECTION1:
    raise ValueError(
        "MONGO_COLLECTION1 environment variable or secret is not set.")

MONGO_COLLECTION2 = get_secret_or_env(
    f"{PROJECT_PREFIX}mongo_collection2", "MONGO_COLLECTION2")
if not MONGO_COLLECTION2:
    raise ValueError(
        "MONGO_COLLECTION2 environment variable or secret is not set.")

CLIENT_ID = get_secret_or_env(f"{PROJECT_PREFIX}client_id", "CLIENT_ID")
if not CLIENT_ID:
    raise ValueError("CLIENT_ID environment variable or secret is not set.")

GUILD_ID = get_secret_or_env(f"{PROJECT_PREFIX}guild_id", "GUILD_ID")
if not GUILD_ID:
    raise ValueError("GUILD_ID environment variable or secret is not set.")

CHANNEL_ID = get_secret_or_env(f"{PROJECT_PREFIX}channel_id", "CHANNEL_ID")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID environment variable or secret is not set.")

DISCORD_BOT_TOKEN = get_secret_or_env(
    f"{PROJECT_PREFIX}discord_bot_token", "DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError(
        "DISCORD_BOT_TOKEN environment variable or secret is not set.")

VPN_USER = get_secret_or_env(f"{PROJECT_PREFIX}vpn_user", "VPN_USER")
if not VPN_USER:
    raise ValueError("VPN_USER environment variable or secret is not set.")

VPN_PASS = get_secret_or_env(f"{PROJECT_PREFIX}vpn_pass", "VPN_PASS")
if not VPN_PASS:
    raise ValueError("VPN_PASS environment variable or secret is not set.")

LOG_LEVEL = get_secret_or_env(
    f"{PROJECT_PREFIX}log_level", "LOG_LEVEL") or "INFO"
if LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise ValueError("Invalid LOG_LEVEL environment variable or secret.")

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
