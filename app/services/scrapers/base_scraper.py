import asyncio
import random
from datetime import datetime, timezone
from typing import Optional
from playwright.async_api import async_playwright
from app.config import HEADERS
from app.services.logger import get_logger

logger = get_logger(__name__)


class ProductInfo:
    """Data class for storing product information."""

    def __init__(
        self,
        name: Optional[str] = None,
        price1: Optional[str] = None,
        price2: Optional[str] = None,
        price3: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> None:
        self.name = name
        self.price1 = price1
        self.price2 = price2
        self.price3 = price3
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def __repr__(self) -> str:
        parts = []
        for attr in ("name", "price1", "price2", "price3", "timestamp"):
            val = getattr(self, attr)
            if val is not None:
                parts.append(f"{attr}={val!r}")
        return f"ProductInfo({', '.join(parts)})"


class BaseScraper:
    """Base class: fetches HTML via Playwright and injects headers/random delay."""

    async def get_page_source(self, url: str) -> str:
        await asyncio.sleep(random.uniform(1, 3))
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=HEADERS["User-Agent"],
                extra_http_headers=HEADERS
            )
            page = await context.new_page()
            await page.goto(url, timeout=60_000)
            content = await page.content()
            await browser.close()
            return content

    async def get_product_info(self, url: str) -> ProductInfo:
        """
        Fetches the page and then calls parse() to extract name + price1/2/3.
        Subclasses **must** override parse(html)->ProductInfo.
        """
        html = await self.get_page_source(url)
        return self.parse(html)

    def parse(self, html: str) -> ProductInfo:
        """Override in subclasses to extract ProductInfo from HTML."""
        raise NotImplementedError("Scraper must implement parse()")
