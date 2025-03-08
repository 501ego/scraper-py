from app.services.database import store_product_info
from app.services.scraper import ParisScraper, FalabellaScraper
from app.services.logger import get_logger
from app.utils.logging import log_product_info
from app.config import service_name, PARIS_LABELS, FALABELLA_LABELS
from app.utils.price_compare import compare_product_prices

logger = get_logger(service_name)

urls_paris = [
    'https://www.paris.cl/apple-watch-series-10-gps-caja-aluminio-negro-azabache-46mm-correa-deportiva-negra-talla-m%2Fl-849062999.html',
    'https://www.paris.cl/apple-macbook-air-chip-m3-cpu-de-8%C2%A0nucleos-gpu-10%C2%A0nucleos-16gb-ram-256gb-ssd-15-medianoche-888446999.html',
    'https://www.paris.cl/apple-macbook-pro-chip-m4-16gb-ram-512gb-ssd-14-color-plata-888448999.html',
]

urls_falabella = [
    'https://www.falabella.com/falabella-cl/product/prod122944127/Apple-Watch-Serie-10-(Gps)-Caja-Aluminio-46mm-Correa-Loop-Deportiva/17268242',
    'https://www.falabella.com/falabella-cl/product/17336907/Apple-MacBook-Air-(13,6-,-M3-(8n-CPU,-8n-GPU),-16GB-RAM,-256GB-SSD)/17336907',
    'https://www.falabella.com/falabella-cl/product/17336911/Apple-MacBook-Air-(15,3-,-M3-(8n-CPU,-10n-GPU),-16GB-RAM,-256GB-SSD)/17336911',
    'https://www.falabella.com/falabella-cl/product/17336918/Apple-MacBook-Pro-(14,2-,-M4-Pro-(12n-CPU,-16n-GPU),-24GB-RAM,-512GB-SSD)/17336918',
    'https://www.falabella.com/falabella-cl/product/17336919/Apple-MacBook-Pro-(14,2-,-M4-(10n-CPU,-10n-GPU),-16GB-RAM,-512GB-SSD)/17336919',

]


def main():
    paris_scraper = ParisScraper()
    falabella_scraper = FalabellaScraper()
    for url in urls_paris:
        info = paris_scraper.get_product_info(url)
        log_product_info("Paris", url, info, PARIS_LABELS)
        compare_product_prices(url, info, PARIS_LABELS)
        store_product_info("Paris", url, info, PARIS_LABELS)
    for url in urls_falabella:
        info = falabella_scraper.get_product_info(url)
        log_product_info("Falabella", url, info, FALABELLA_LABELS)
        compare_product_prices(url, info, FALABELLA_LABELS)
        store_product_info("Falabella", url, info, FALABELLA_LABELS)


if __name__ == "__main__":
    main()
