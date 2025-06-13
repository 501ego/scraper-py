from bs4 import BeautifulSoup
from app.services.scrapers.base_scraper import BaseScraper, ProductInfo
from app.services.logger import get_logger

logger = get_logger(__name__)


class SpDigitalScraper(BaseScraper):
    """Scrapes SP Digital pages for three payment-method prices."""

    def _extract(self, container, text, updating=False):
        lbl = container.find("span", string=lambda s: s and text in s)
        if not lbl:
            return None
        if updating:
            pc = lbl.find_next(
                "span", class_="product-detail-module--updatingPriceContainer--mq+El")
            elm = pc and pc.find("span")
        else:
            elm = lbl.find_next_sibling("span")
        if elm:
            txt = elm.get_text(strip=True)
            return txt if "$" in txt else None
        return None

    def parse(self, html: str) -> ProductInfo:
        soup = BeautifulSoup(html, "html.parser")
        name_el = soup.find(
            "h1", class_=lambda c: c and "product-detail-module--productName" in c)
        name = name_el.get_text(strip=True) if name_el else None

        cont = soup.find(
            "div", class_="product-detail-module--priceContainer--DKoen")
        if not cont:
            return ProductInfo(name, None, None, None)

        p1 = self._extract(cont, "Normal", updating=False)
        p2 = self._extract(cont, "Pago con transferencia", updating=True)
        p3 = self._extract(cont, "Otros medios de pago", updating=True)
        return ProductInfo(name, p1, p2, p3)
