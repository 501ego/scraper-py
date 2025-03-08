from app.services.scraper import ProductInfo
from app.services.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)


def log_product_info(prefix: str, url: str, info: ProductInfo, label_mapping: dict) -> None:
    if not info.name:
        logger.warning(
            "%s: No valid product info extracted from URL: %s", prefix, url)
        return
    border = "-" * 60
    header = f"{prefix} Product Info".center(60)
    url_line = f"URL: {url}"
    info_lines = []
    for field, label in label_mapping.items():
        value = getattr(info, field, None)
        if value is not None:
            info_lines.append(f"{label:<20}: {value}")
    message = f"\n{border}\n{header}\n{url_line}\n{'-' * 60}\n" + \
        "\n".join(info_lines) + f"\n{border}"
    logger.info(message)
