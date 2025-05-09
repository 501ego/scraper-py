import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from app.utils.json_parser import extract_product_json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from app.config import HEADERS, service_name
from app.services.logger import get_logger
import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

logger = get_logger(service_name)


@dataclass
class ProductInfo:
    """Data class for storing product information.

    Fields with a None value will be omitted from the object's string representation.
    """

    def __init__(self, name: Optional[str] = None, price1: Optional[str] = None,
                 price2: Optional[str] = None, price3: Optional[str] = None,
                 timestamp: str = "") -> None:
        self.name = name
        self.price1 = price1
        self.price2 = price2
        self.price3 = price3
        self.timestamp = timestamp

    def __repr__(self) -> str:
        fields = []
        if self.name is not None:
            fields.append(f"name={self.name!r}")
        if self.price1 is not None:
            fields.append(f"price1={self.price1!r}")
        if self.price2 is not None:
            fields.append(f"price2={self.price2!r}")
        if self.price3 is not None:
            fields.append(f"price3={self.price3!r}")
        if self.timestamp:
            fields.append(f"timestamp={self.timestamp!r}")
        return f"ProductInfo({', '.join(fields)})"


class BaseScraper:
    """Base class for scrapers. Uses Playwright to fetch page source."""

    def __init__(self) -> None:
        # load_cookies_from_json(self.scraper)
        pass

    async def get_page_source(self, url: str) -> str:
        await asyncio.sleep(random.uniform(1, 3))
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=HEADERS.get("User-Agent"),
                extra_http_headers=HEADERS
            )
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
            await browser.close()
            return content


class PageRetrievalError(Exception):
    """Custom exception raised when a page cannot be retrieved after retries."""
    pass


class FalabellaScraper(BaseScraper):
    """Scraper for Falabella with retry logic that returns ProductInfo objects."""

    async def get_page_source(self, url: str) -> str:
        max_retries = 2
        for attempt in range(max_retries):
            await asyncio.sleep(random.uniform(1, 3))
            try:
                text = await super().get_page_source(url)
            except Exception as e:
                logger.debug(
                    "Attempt %s: Exception obtaining page: %s", attempt+1, e)
                await asyncio.sleep(random.uniform(3, 6))
                continue
            if text and "captcha" not in text.lower():
                return text
            else:
                logger.debug(
                    "Attempt %s: Page content did not pass validation.", attempt+1)
                await asyncio.sleep(random.uniform(3, 6))
        logger.error("Failed to retrieve page after %s attempts.", max_retries)
        raise PageRetrievalError(
            f"Failed to retrieve page after {max_retries} attempts for URL: {url}")

    def parse(self, html: str) -> ProductInfo:
        soup = BeautifulSoup(html, 'html.parser')

        name_element = soup.find(
            "h1", class_=lambda c: c and "product-name" in c)
        name = name_element.get_text(strip=True) if name_element else None

        prices_container = soup.find(
            "ol",
            class_="jsx-3339469769 ol-4_GRID pdp-prices fa--prices li-separation"
        )

        price_cmr = None
        price_internet = None
        price_normal = None

        if prices_container:
            li_cmr = prices_container.find(
                "li", attrs={"data-cmr-price": True})
            price_cmr = li_cmr.get("data-cmr-price") if li_cmr else None
            li_internet = prices_container.find(
                "li", attrs={"data-internet-price": True})
            if li_internet:
                price_internet = li_internet.get("data-internet-price")
            else:
                li_event = prices_container.find(
                    "li", attrs={"data-event-price": True})
                price_internet = li_event.get(
                    "data-event-price") if li_event else None

            li_normal = prices_container.find(
                "li", attrs={"data-normal-price": True})
            price_normal = li_normal.get(
                "data-normal-price") if li_normal else None

        return ProductInfo(
            name=name,
            price1=price_cmr,
            price2=price_internet,
            price3=price_normal,
            timestamp=datetime.now().isoformat()
        )

    async def get_product_info(self, url: str) -> ProductInfo:
        html = await self.get_page_source(url)
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
            price3 = None
            for entry in prices:
                price_book_id = entry.get("priceBookId", "")
                if price_book_id == "clp-cencosud-prices":
                    price1 = entry.get("price")
                elif price_book_id == "clp-internet-prices":
                    price2 = entry.get("price")
                elif price_book_id == "clp-list-prices":
                    price3 = entry.get("price")
            result = ProductInfo(
                name=name,
                price1=price1,
                price2=price2,
                price3=price3,
                timestamp=datetime.now().isoformat()
            )
            logger.debug("Final result: %s", result)
            return result
        else:
            logger.debug(
                "Could not extract JSON. Returning empty ProductInfo.")
            return ProductInfo(name=None, price1=None, price2=None, price3=None,
                               timestamp=datetime.now().isoformat())

    async def get_product_info(self, url: str) -> ProductInfo:
        html = await self.get_page_source(url)
        logger.debug("HTML length: %s", len(html))
        return self.parse(html)


class SpDigitalScraper(BaseScraper):
    """
    Scraper for SP Digital that extracts product data from the page source.
    Relevant price values:
      - Normal: The original price (displayed with a strikethrough)
      - Pago con transferencia: Price when paying via bank transfer
      - Otros medios de pago: Price for other payment methods
    """

    def _extract_price(self, container, label_text, mode="sibling"):
        """Extract price based on a label and search mode."""
        label_elem = container.find(
            "span", string=lambda s: s and label_text in s)
        if not label_elem:
            return None

        price_elem = None
        if mode == "sibling":
            price_elem = label_elem.find_next_sibling("span")
        elif mode == "updating":
            price_container = label_elem.find_next(
                "span", class_="product-detail-module--updatingPriceContainer--mq+El")
            if price_container:
                price_elem = price_container.find("span")

        if price_elem and "$" in price_elem.get_text():
            return price_elem.get_text(strip=True)
        return None

    def parse(self, html: str) -> ProductInfo:
        soup = BeautifulSoup(html, 'html.parser')

        name_element = soup.find(
            "h1", class_=lambda c: c and "product-detail-module--productName" in c)
        name = name_element.get_text(strip=True) if name_element else None

        container = soup.find(
            "div", class_="product-detail-module--priceContainer--DKoen")
        if not container:
            return ProductInfo(name=name, timestamp=datetime.now().isoformat())

        price_normal = self._extract_price(container, "Normal", mode="sibling")
        price_transfer = self._extract_price(
            container, "Pago con transferencia", mode="updating")
        price_other = self._extract_price(
            container, "Otros medios de pago", mode="updating")

        return ProductInfo(
            name=name,
            price1=price_normal,
            price2=price_transfer,
            price3=price_other,
            timestamp=datetime.now().isoformat()
        )

    async def get_product_info(self, url: str) -> ProductInfo:
        html = await self.get_page_source(url)
        return self.parse(html)
