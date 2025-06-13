import asyncio
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper, ProductInfo
from app.services.logger import get_logger

logger = get_logger(__name__)


class PageRetrievalError(Exception):
    pass


class FalabellaScraper(BaseScraper):
    """Scraper for Falabella.com with captcha-retry logic."""

    async def get_page_source(self, url: str) -> str:
        max_retries = 2
        for i in range(max_retries):
            html = await super().get_page_source(url)
            if "captcha" not in html.lower():
                return html
            logger.debug("Falabella captcha detected, retry %d/%d",
                         i+1, max_retries)
            await asyncio.sleep(3)
        raise PageRetrievalError(f"Failed to fetch Falabella page: {url}")

    def parse(self, html: str) -> ProductInfo:
        soup = BeautifulSoup(html, "html.parser")
        name_el = soup.find("h1", class_=lambda c: c and "product-name" in c)
        name = name_el.get_text(strip=True) if name_el else None

        p1 = p2 = p3 = None
        ol = soup.find("ol", class_=lambda c: c and "pdp-prices" in c)
        if ol:
            for li in ol.find_all("li"):
                attrs = li.attrs
                if "data-cmr-price" in attrs:
                    p1 = attrs["data-cmr-price"]
                elif "data-internet-price" in attrs or "data-event-price" in attrs:
                    p2 = attrs.get(
                        "data-internet-price") or attrs.get("data-event-price")
                elif "data-normal-price" in attrs:
                    p3 = attrs["data-normal-price"]

        return ProductInfo(name, p1, p2, p3)
