import re
from typing import Optional
from app.services.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)


def parse_price(price: Optional[str]) -> Optional[int]:
    """Parses a price string or number and returns its integer value, or None if conversion fails."""
    if price is None:
        return None
    price_str = str(price)
    num_str = re.sub(r"[^\d]", "", price_str)

    try:
        return int(num_str)
    except Exception as e:
        logger.error("Error parsing price '%s': %s", price_str, e)
        return None
