import asyncio
from dateutil import parser
import discord
from pymongo import DESCENDING
from app.services.database import get_urls_by_source, store_product_info, info_collection
from app.services.scraper import ParisScraper, FalabellaScraper, ProductInfo
from app.utils.price_parser import parse_price
from app.config import PRICE_FIELDS, PARIS_LABELS, FALABELLA_LABELS, service_name, SOURCES
from app.services.logger import get_logger

logger = get_logger(service_name)


def format_price(value: int) -> str:
    return f"${value:,.0f}".replace(",", ".") if value else "No disponible"


def get_previous_product_info(url: str):
    return info_collection.find_one({"url": url}, sort=[("timestamp", DESCENDING)])


def compare_product_prices(url: str, new_info: ProductInfo, label_mapping: dict) -> None:
    stored = get_previous_product_info(url)
    if not stored:
        logger.debug(
            "No previous record found for comparison for URL: %s", url)
        return

    for field in PRICE_FIELDS:
        field_label = label_mapping.get(field, field)
        new_price = parse_price(getattr(new_info, field))
        stored_price = stored.get(field_label)
        if new_price is None or stored_price is None:
            continue
        if new_price > stored_price:
            logger.info("For URL %s, %s increased from %s to %s",
                        url, field_label, stored_price, new_price)
        elif new_price < stored_price:
            logger.info("For URL %s, %s decreased from %s to %s",
                        url, field_label, stored_price, new_price)
        else:
            logger.info("For URL %s, %s remains unchanged at %s",
                        url, field_label, new_price)


def format_comparison_details(url: str, new_info: ProductInfo, label_mapping: dict) -> str:
    try:
        ts = parser.parse(new_info.timestamp)
        formatted_ts = ts.strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        formatted_ts = new_info.timestamp

    info_section = ""
    for field in PRICE_FIELDS:
        price = parse_price(getattr(new_info, field))
        label = label_mapping.get(field, field)
        info_section += f"**{label}:** {format_price(price)}\n"

    info_section += f"**Fecha:** {formatted_ts}\n\n"

    changes = ""
    stored = get_previous_product_info(url)
    if stored:
        for field in PRICE_FIELDS:
            field_label = label_mapping.get(field, field)
            new_price = parse_price(getattr(new_info, field))
            stored_price = stored.get(field_label)
            if new_price is None or stored_price is None:
                continue
            if new_price > stored_price:
                changes += f"🟢 **{field_label}** aumentó de {format_price(stored_price)} a {format_price(new_price)}\n\n"
            elif new_price < stored_price:
                changes += f"🔴 **{field_label}** bajó de {format_price(stored_price)} a {format_price(new_price)}\n\n"

    if not changes:
        changes = "**No se detectaron cambios en los precios.**"

    return info_section + changes


async def create_embed_for_url(source: str, url: str, scraper, label_mapping: dict, bot: discord.Client = None) -> discord.Embed:
    try:
        info = await scraper.get_product_info(url)
    except Exception as e:
        logger.error("Error getting product info for %s: %s", url, e)
        return None

    details = format_comparison_details(url, info, label_mapping)
    compare_product_prices(url, info, label_mapping)

    store_product_info(source, url, info, label_mapping)

    if not details:
        return None

    title = f"{source} - {info.name}" if info.name else f"{source} - Producto desconocido"
    embed = discord.Embed(title=title, description=details,
                          url=url, color=0x2ecc71)

    if bot is not None:
        embed.set_footer(
            text=f"Generado por {bot.user.name}", icon_url=bot.user.display_avatar.url)
    return embed


async def get_comparison_embeds(bot: discord.Client = None) -> list:
    tasks = []
    for source in SOURCES:
        scraper = ParisScraper() if source.lower() == "paris" else FalabellaScraper()
        label_mapping = PARIS_LABELS if source.lower() == "paris" else FALABELLA_LABELS

        urls = get_urls_by_source(source)
        for url in urls:
            tasks.append(create_embed_for_url(
                source, url, scraper, label_mapping, bot))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [embed for embed in results if embed is not None and not isinstance(embed, Exception)]
