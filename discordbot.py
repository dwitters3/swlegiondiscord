import os
import discord
import asyncio
import feedparser
import cloudscraper
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
FEED_URL = "https://forums.atomicmassgames.com/discover/22.xml/?member=1073&key=192dbc97e9d6e03aa0528ea0f4b48e65"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_post_id = None

async def fetch_feed():
    scraper = cloudscraper.create_scraper()
    content = await asyncio.to_thread(scraper.get, FEED_URL)
    print(content.content)
    return feedparser.parse(content.content)

@tasks.loop(minutes=5)
async def check_new_posts():
    global last_post_id
    print(last_post_id)
    feed = await fetch_feed()
    if not feed.entries:
        return
    latest_entry = feed.entries[0]
    if last_post_id is None:
        last_post_id = latest_entry.id
        return
    if latest_entry.id != last_post_id:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(f"New post: {latest_entry.title}\n{latest_entry.link}")
        last_post_id = latest_entry.id

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_new_posts.start()

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)