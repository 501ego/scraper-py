import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from app.utils.json_parser import extract_product_json
import cloudscraper
from bs4 import BeautifulSoup

from app.config import HEADERS, BROWSER, service_name
from app.utils.logger import get_logger

logger = get_logger(service_name)


@dataclass
class ProductInfo:
    """Data class for storing product information.

    Fields with a None value will be omitted from the object's string representation.
    """

    def __init__(self, name: Optional[str] = None, price1: Optional[str] = None,
                 price2: Optional[str] = None, old_price: Optional[str] = None,
                 timestamp: str = "") -> None:
        self.name = name
        self.price1 = price1
        self.price2 = price2
        self.old_price = old_price
        self.timestamp = timestamp

    def __repr__(self) -> str:
        fields = []
        if self.name is not None:
            fields.append(f"name={self.name!r}")
        if self.price1 is not None:
            fields.append(f"price1={self.price1!r}")
        if self.price2 is not None:
            fields.append(f"price2={self.price2!r}")
        if self.old_price is not None:
            fields.append(f"old_price={self.old_price!r}")
        if self.timestamp:
            fields.append(f"timestamp={self.timestamp!r}")
        return f"ProductInfo({', '.join(fields)})"


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
    """Scraper for Falabella with retry logic that returns ProductInfo objects."""

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

    def parse(self, html: str) -> ProductInfo:
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

        return ProductInfo(
            name=name,
            price1=price_cmr,
            price2=price_internet,
            old_price=None,
            timestamp=datetime.now().isoformat()
        )

    def get_product_info(self, url: str) -> ProductInfo:
        html = self.get_page_source(url)
        return self.parse(html)


class ParisScraper(BaseScraper):
    """Scraper for Paris that extracts product data from embedded JSON and returns a ProductInfo object."""

    def parse(self, html: str) -> ProductInfo:
        product_data = extract_product_json(html)
        if product_data:
            name = product_data.get("name")
            prices: List[Dict[str, str]] = product_data.get("prices", [])
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
            result = ProductInfo(
                name=name,
                price1=price1,
                price2=price2,
                old_price=old_price,
                timestamp=datetime.now().isoformat()
            )
            logger.debug("Final result: %s", result)
            return result
        else:
            logger.debug(
                "Could not extract JSON. Returning empty ProductInfo.")
            return ProductInfo(
                name=None,
                price1=None,
                price2=None,
                old_price=None,
                timestamp=datetime.now().isoformat()
            )

    def get_product_info(self, url: str) -> ProductInfo:
        html = self.get_page_source(url)
        logger.debug("HTML length: %s", len(html))
        return self.parse(html)
