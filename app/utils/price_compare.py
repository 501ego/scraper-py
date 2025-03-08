import re
from typing import Optional
from app.services.logger import get_logger
from app.services.scraper import ProductInfo
from app.config import PRICE_FIELDS, service_name

logger = get_logger(service_name)


def parse_price(price: str) -> Optional[int]:
    if not price:
        return None
    num_str = re.sub(r"[^\d]", "", price)
    try:
        return int(num_str)
    except Exception as e:
        logger.error("Error parsing price '%s': %s", price, e)
        return None


def compare_product_prices(url: str, new_info: ProductInfo, label_mapping: dict) -> None:
    from app.services.database import collection
    stored = collection.find_one({"url": url})
    if not stored:
        logger.warning("No record found for URL: %s", url)
        return
    for field in PRICE_FIELDS:
        field_label = label_mapping.get(field, field)
        new_price = parse_price(getattr(new_info, field))
        stored_price = parse_price(stored.get(field_label))
        if new_price is None or stored_price is None:
            continue
        if new_price > stored_price:
            logger.info("For URL %s, %s increased from %s to %s",
                        url, field_label, stored_price, new_price)
        elif new_price < stored_price:
            logger.info("For URL %s, %s decreased from %s to %s",
                        url, field_label, stored_price, new_price)
        else:
            logger.info("For URL %s, %s remains unchanged at %s",
                        url, field_label, new_price)
