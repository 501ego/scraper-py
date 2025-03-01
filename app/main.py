from app.services.scraper import ParisScraper, FalabellaScraper
from app.utils.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)

urls_paris = ['https://www.paris.cl/apple-macbook-pro-chip-m4-16gb-ram-512gb-ssd-14-color-plata-888448999.html',
              'https://www.paris.cl/apple-watch-series-10-gps-caja-aluminio-negro-azabache-46mm-correa-deportiva-negra-talla-m%2Fl-849062999.html',
              'https://www.paris.cl/apple-macbook-air-chip-m3-cpu-de-8%C2%A0nucleos-gpu-10%C2%A0nucleos-16gb-ram-256gb-ssd-15-medianoche-888446999.html', 'https://www.paris.cl/listas/macbook/'
              ]

urls_falabella = [
    'https://www.falabella.com/falabella-cl/product/17336907/Apple-MacBook-Air-(13,6-,-M3-(8n-CPU,-8n-GPU),-16GB-RAM,-256GB-SSD)/17336907',
]

# Scrape Paris product info.
paris_scraper = ParisScraper()
for url in urls_paris:
    info = paris_scraper.get_product_info(url)
    logger.info("URL: %s", url)
    logger.info("Product Name: %s", info.get("name"))
    logger.info("Price: %s", info.get("price1"))
    logger.info("Price 2: %s", info.get("price2"))
    logger.info("Old price: %s", info.get("old_price"))
    logger.info("Timestamp: %s", info.get("timestamp"))
    logger.info("------------")

# Scrape Falabella product info.
falabella_scraper = FalabellaScraper()
for url in urls_falabella:
    info = falabella_scraper.get_product_info(url)
    logger.info("URL: %s", url)
    logger.info("Product Name: %s", info.get("name"))
    logger.info("Price CMR: %s", info.get("price_cmr"))
    logger.info("Price normal: %s", info.get("price_internet"))
    logger.info("Timestamp: %s", info.get("timestamp"))
    logger.info("------------")
