from app.services.scraper import ParisScraper, FalabellaScraper
from app.utils.logger import get_logger
from app.config import service_name
from app.services.scraper import ProductInfo

logger = get_logger(service_name)

urls_paris = [
    'https://www.paris.cl/apple-macbook-pro-chip-m4-16gb-ram-512gb-ssd-14-color-plata-888448999.html',
    'https://www.paris.cl/apple-watch-series-10-gps-caja-aluminio-negro-azabache-46mm-correa-deportiva-negra-talla-m%2Fl-849062999.html',
    'https://www.paris.cl/apple-macbook-air-chip-m3-cpu-de-8%C2%A0nucleos-gpu-10%C2%A0nucleos-16gb-ram-256gb-ssd-15-medianoche-888446999.html',
    'https://www.paris.cl/listas/macbook/'
]

urls_falabella = [
    'https://www.falabella.com/falabella-cl/product/17336907/Apple-MacBook-Air-(13,6-,-M3-(8n-CPU,-8n-GPU),-16GB-RAM,-256GB-SSD)/17336907', 'https://www.falabella.com/falabella-cl/product/prod122944127/Apple-Watch-Serie-10-(Gps)-Caja-Aluminio-46mm-Correa-Loop-Deportiva/17268242'
]


def log_product_info(prefix: str, url: str, info: ProductInfo) -> None:
    """
    Logs product information using a global logger.
    Fields with a None value are omitted from the log message.
    Price 1 represents the card price and Price 2 represents the normal price.
    """
    if not info.name:
        logger.warning(
            "%s: No valid product info extracted from URL: %s", prefix, url)
        return

    lines = [
        "=" * 38,
        f"{prefix} Product Info",
        f"URL: {url}",
        f"Product Name: {info.name}"
    ]
    if info.price1 is not None:
        lines.append(f"Price with Card: {info.price1}")
    if info.price2 is not None:
        lines.append(f"Normal Price: {info.price2}")
    if info.old_price is not None:
        lines.append(f"Old Price: {info.old_price}")
    if info.timestamp:
        lines.append(f"Timestamp: {info.timestamp}")
    lines.append("=" * 38)

    message = "\n".join(lines)
    logger.info(message)


# Scrape Paris product info.
paris_scraper = ParisScraper()
for url in urls_paris:
    info = paris_scraper.get_product_info(url)
    log_product_info("Paris", url, info)

# Scrape Falabella product info.
falabella_scraper = FalabellaScraper()
for url in urls_falabella:
    info = falabella_scraper.get_product_info(url)
    log_product_info("Falabella", url, info)
