import discord
from discord.ext import tasks
from app.services.database import get_all_urls, store_product_info
from app.utils.price_comparer import get_previous_product_info
from app.services.scraper import ParisScraper, FalabellaScraper
from app.utils.price_parser import parse_price
from app.config import PRICE_FIELDS, PARIS_LABELS, FALABELLA_LABELS, CHANNEL_ID, service_name
from app.services.logger import get_logger
from dateutil import parser

logger = get_logger(service_name)


def format_price(value: int) -> str:
    return f"${value:,.0f}".replace(",", ".") if value else "Not available"


class PriceWatcher:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.channel_id = CHANNEL_ID
        self.scrapers = {
            'paris': (ParisScraper(), PARIS_LABELS),
            'falabella': (FalabellaScraper(), FALABELLA_LABELS)
        }
        self.channel = None

    @tasks.loop(hours=2)
    async def watch_prices(self):
        if self.channel is None:
            logger.error("Channel is None. Task cannot run.")
            return

        urls_grouped = get_all_urls()

        for source_group in urls_grouped:
            source = source_group['source'].lower()
            scraper, labels = self.scrapers.get(source, (None, None))

            if scraper is None:
                logger.warning("No scraper found for source %s", source)
                continue

            for url in source_group['urls']:
                await self.process_url(source, url, scraper, labels, self.channel)

    async def process_url(self, source, url, scraper, labels, channel):
        try:
            new_info = await scraper.get_product_info(url)
            last_info = get_previous_product_info(url)

            if last_info is None:
                store_product_info(source, url, new_info, labels)
                return

            embed_desc = ""

            for field in PRICE_FIELDS:
                label = labels.get(field, field)
                new_price = parse_price(getattr(new_info, field))
                old_price = last_info.get(label)

                if new_price != old_price and new_price is not None and old_price is not None:
                    arrow = "🔻 Decreased" if new_price < old_price else "🔺 Increased"
                    embed_desc += f"{arrow} **{label}** from {format_price(old_price)} to {format_price(new_price)}\n"

            if embed_desc:
                ts = parser.parse(new_info.timestamp)
                formatted_ts = ts.strftime("%d/%m/%Y %H:%M:%S")

                embed = discord.Embed(
                    title=f"{source.capitalize()} - {new_info.name}",
                    description=embed_desc,
                    url=url,
                    color=0x3498db
                )
                embed.set_footer(text=f"Updated at {formatted_ts}")

                await channel.send(embed=embed)
                store_product_info(source, url, new_info, labels)

        except Exception as e:
            logger.error("Error while processing URL %s: %s", url, e)

    @watch_prices.before_loop
    async def before_watch_prices(self):
        await self.bot.wait_until_ready()
        self.channel = await self.bot.fetch_channel(self.channel_id)
        if self.channel:
            logger.debug(
                f"Price watcher ready, using channel {self.channel.name} ({self.channel.id}).")
        else:
            logger.error("Channel is None. Task cannot run.")
