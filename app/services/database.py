from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION, service_name, PRICE_FIELDS
from app.services.logger import get_logger
from app.services.scraper import ProductInfo
from app.utils.price_compare import parse_price

logger = get_logger(service_name)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
collection.create_index("url")


def has_valid_price(new_info: ProductInfo) -> bool:
    for field in PRICE_FIELDS:
        if parse_price(getattr(new_info, field)):
            return True
    return False


def should_store_product_info(url: str, new_info: ProductInfo, label_mapping: dict) -> bool:
    latest_cursor = collection.find({"url": url}).sort(
        label_mapping.get("timestamp", "timestamp"), -1).limit(1)
    latest_doc = next(latest_cursor, None)
    if not latest_doc:
        return True
    for field in PRICE_FIELDS:
        field_label = label_mapping.get(field, field)
        new_price = parse_price(getattr(new_info, field))
        stored_price = parse_price(latest_doc.get(field_label))
        if new_price is None or stored_price is None:
            continue
        if new_price != stored_price:
            return True
    return False


def store_product_info(prefix: str, url: str, info: ProductInfo, label_mapping: dict) -> None:
    if not has_valid_price(info):
        logger.warning("No valid prices for URL: %s. Skipping storage.", url)
        return
    if not should_store_product_info(url, info, label_mapping):
        logger.debug(
            "No price change detected for URL: %s. Skipping storage.", url)
        return
    document = {"prefix": prefix, "url": url}
    for field, label in label_mapping.items():
        document[label] = getattr(info, field)
    try:
        result = collection.insert_one(document)
        logger.debug("Inserted product info with id: %s", result.inserted_id)
    except Exception as e:
        logger.error("Error inserting document for %s: %s", url, e)
