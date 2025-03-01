import time
from datetime import datetime
from typing import Optional, Dict
import cloudscraper
from bs4 import BeautifulSoup
from app.config import HEADERS, BROWSER
from app.utils.json_processor import extract_product_json
from app.utils.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)


class BaseScraper:
    """Base class for scrapers."""

    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper(browser=BROWSER)

    def get_page_source(self, url: str) -> str:
        response = self.scraper.get(url, headers=HEADERS)
        if response.status_code != 200:
            logger.error("Error obtaining page, status code: %s",
                         response.status_code)
        return response.text


class FalabellaScraper(BaseScraper):
    """Scraper for Falabella with retry logic."""

    def get_page_source(self, url: str) -> str:
        max_retries = 3
        last_status = None
        for attempt in range(max_retries):
            response = self.scraper.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.text
            else:
                logger.debug("Attempt %s: Error obtaining page, status code: %s",
                             attempt + 1, response.status_code)
                last_status = response.status_code
                time.sleep(3)
        logger.error("Error obtaining page, status code: %s", last_status)
        return ""

    def parse(self, html: str) -> Dict[str, Optional[str]]:
        soup = BeautifulSoup(html, 'html.parser')
        name_element = soup.select_one(
            'h1.jsx-783883818.product-name.fa--product-name.false')
        name = name_element.get_text(strip=True) if name_element else None
        li_cmr = soup.find("li", attrs={"data-cmr-price": True})
        li_internet = soup.find("li", attrs={"data-internet-price": True})
        price_cmr = li_cmr.find("span").get_text(
            strip=True) if li_cmr and li_cmr.find("span") else None
        price_internet = li_internet.find("span").get_text(
            strip=True) if li_internet and li_internet.find("span") else None
        return {
            "name": name,
            "price_cmr": price_cmr,
            "price_internet": price_internet,
            "timestamp": datetime.now().isoformat()
        }

    def get_product_info(self, url: str) -> Dict[str, Optional[str]]:
        html = self.get_page_source(url)
        return self.parse(html)


class ParisScraper(BaseScraper):
    """Scraper for Paris that extracts product data from embedded JSON."""

    def parse(self, html: str) -> Dict[str, Optional[str]]:
        product_data = extract_product_json(html)
        if product_data:
            name = product_data.get("name")
            prices = product_data.get("prices", [])
            price1 = None
            price2 = None
            old_price = None
            for entry in prices:
                price_book_id = entry.get("priceBookId", "")
                if price_book_id == "clp-cencosud-prices":
                    price1 = entry.get("price")
                elif price_book_id == "clp-internet-prices":
                    price2 = entry.get("price")
                elif price_book_id == "clp-list-prices":
                    old_price = entry.get("price")
            result = {
                "name": name,
                "price1": price1,
                "price2": price2,
                "old_price": old_price,
                "timestamp": datetime.now().isoformat()
            }
            logger.debug("Final result: %s", result)
            return result
        else:
            logger.debug("Could not extract JSON. Returning empty results.")
            return {
                "name": None,
                "price1": None,
                "price2": None,
                "old_price": None,
                "timestamp": datetime.now().isoformat()
            }

    def get_product_info(self, url: str) -> Dict[str, Optional[str]]:
        html = self.get_page_source(url)
        logger.debug("HTML length: %s", len(html))
        return self.parse(html)
