import datetime
from pymongo import MongoClient, DESCENDING
from app.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION1, MONGO_COLLECTION2, service_name, PRICE_FIELDS
from app.services.logger import get_logger
from app.services.scrapers.base_scraper import ProductInfo
from app.utils.price_parser import parse_price

logger = get_logger(service_name)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

info_collection = db[MONGO_COLLECTION1]
info_collection.create_index([("url", DESCENDING), ("timestamp", DESCENDING)])
urls_collection = db[MONGO_COLLECTION2]
urls_collection.create_index("source", unique=True)


def has_valid_price(new_info: ProductInfo) -> bool:
    "Checks if the ProductInfo object contains at least one valid price."
    for field in PRICE_FIELDS:
        if parse_price(getattr(new_info, field)):
            return True
    return False


def should_store_product_info(url: str, new_info: ProductInfo, label_mapping: dict) -> bool:
    """Determines if new product info should be stored based on price changes."""
    latest_doc = info_collection.find_one(
        {"url": url}, sort=[("timestamp", DESCENDING)])
    if not latest_doc:
        logger.debug(
            "No previous document found for URL: %s. Will store new info.", url)
        return True

    for field in PRICE_FIELDS:
        label = label_mapping.get(field, field)
        new_price = parse_price(getattr(new_info, field))
        stored_price = latest_doc.get(label)

        if new_price is None or stored_price is None:
            continue

        if new_price != stored_price:
            logger.debug(
                "Price change detected for URL: %s (Field: %s, Old: %s, New: %s)",
                url, label, stored_price, new_price
            )
            return True

    logger.debug("No price changes detected for URL: %s.", url)
    return False


def store_product_info(prefix: str, url: str, info: ProductInfo, label_mapping: dict) -> None:
    """Stores the product information as a new document whenever prices change, keeping historical records."""
    if not has_valid_price(info):
        logger.warning("No valid prices for URL: %s. Skipping storage.", url)
        return

    if not should_store_product_info(url, info, label_mapping):
        logger.debug("No price changes for URL: %s. Skipping storage.", url)
        return

    document = {
        "prefix": prefix,
        "url": url,
        "timestamp": datetime.datetime.fromisoformat(info.timestamp),
        "product_name": info.name
    }

    for field in PRICE_FIELDS:
        label = label_mapping.get(field, field)
        raw = getattr(info, field)
        price = parse_price(raw)

        if price is None:
            document[label] = None
        elif price < 1e15:
            document[label] = price
        else:
            logger.warning(
                "Price too large for field %s on URL %s: %s", label, url, price
            )
            document[label] = None

    try:
        result = info_collection.insert_one(document)
        logger.info("Inserted new price record with id: %s for URL: %s",
                    result.inserted_id, url)
    except Exception as e:
        logger.error(
            "Failed to insert document for URL: %s. Error: %s", url, e)


def add_url(source: str, url: str) -> None:
    "Adds a URL to the list for the given source."
    doc = urls_collection.find_one({"source": source})
    if doc:
        if url not in doc.get("urls", []):
            urls_collection.update_one(
                {"source": source}, {"$push": {"urls": url}})
            return url
    else:
        urls_collection.insert_one({"source": source, "urls": [url]})
        return url
    return None


def update_url(source: str, old_url: str, new_url: str) -> None:
    "Updates an existing URL in the list for the given source."
    urls_collection.update_one({"source": source, "urls": old_url}, {
                               "$set": {"urls.$": new_url}})


def delete_url(source: str, url: str) -> None:
    "Deletes a URL from the list for the given source."
    urls_collection.update_one({"source": source}, {"$pull": {"urls": url}})


def get_urls_by_source(source: str) -> list:
    "Retrieves the list of URLs for the given source."
    doc = urls_collection.find_one({"source": source})
    if doc:
        return doc.get("urls", [])
    return []


def get_all_urls() -> list:
    "Retrieves all URL documents grouped by source."
    return list(urls_collection.find({}))
