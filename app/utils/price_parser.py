import re
from typing import Optional
from app.services.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)


def parse_price(price: str) -> Optional[int]:
    "Parses a price string and returns its integer value, or None if conversion fails."
    if not price:
        return None
    num_str = re.sub(r"[^\d]", "", price)
    try:
        return int(num_str)
    except Exception as e:
        logger.error("Error parsing price '%s': %s", price, e)
        return None
