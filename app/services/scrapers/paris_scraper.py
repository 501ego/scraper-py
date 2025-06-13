import json
from typing import Optional
from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper, ProductInfo
from app.utils.json_parser import extract_product_json
from app.services.logger import get_logger

logger = get_logger(__name__)


class ParisScraper(BaseScraper):
    """Scraper for Paris.cl: JSON → JSON-LD → DOM fallback."""

    def parse(self, html: str) -> ProductInfo:
        result = self._parse_embedded_json(html)
        if result:
            return result
        result = self._parse_ld_json(html)
        if result:
            return result
        return self._parse_dom_fallback(html)

    def _parse_embedded_json(self, html: str) -> Optional[ProductInfo]:
        pd = extract_product_json(html)
        if not pd or "prices" not in pd:
            return None

        name = pd.get("name")
        prices = {e.get("priceBookId"): e.get("price") for e in pd["prices"]}
        return ProductInfo(
            name,
            prices.get("clp-cencosud-prices"),
            prices.get("clp-internet-prices"),
            prices.get("clp-list-prices")
        )

    def _parse_ld_json(self, html: str) -> Optional[ProductInfo]:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(tag.string or "")
            except json.JSONDecodeError:
                continue
            if data.get("@type") != "Product":
                continue

            name = data.get("name")
            offers = data.get("offers") or []
            if not isinstance(offers, list):
                offers = [offers]
            extracted = [str(o.get("price")) if o.get("price") is not None else None
                         for o in offers[:3]]
            p1, p2, p3 = (extracted + [None, None, None])[:3]
            return ProductInfo(name, p1, p2, p3)

        return None

    def _parse_dom_fallback(self, html: str) -> ProductInfo:
        soup = BeautifulSoup(html, "html.parser")
        p3_el = soup.select_one(".product-detail__price--list .price")
        p3 = p3_el.get_text(strip=True) if p3_el else None
        return ProductInfo(None, None, None, p3)
