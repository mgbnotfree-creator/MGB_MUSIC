# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# All rights reserved.
# ==========================================================
import asyncio
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import List

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Configure logging
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)

# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)

logger = logging.getLogger("MGBMUSIC")

# Version
__version__ = "3.0.1"

# Load configuration
from config import Config

config = Config()
config.check()

# Global task list for background tasks
tasks: List = []
boot: float = time.time()

# Initialize bot client
from MGBMUSIC.core.bot import Bot
app = Bot()

# Ensure required directories exist
from MGBMUSIC.core.dir import ensure_dirs
ensure_dirs()

# Initialize userbot/assistant clients
from MGBMUSIC.core.userbot import Userbot
userbot = Userbot()

# Initialize database connection
from MGBMUSIC.core.mongo import MongoDB
db = MongoDB()

# Initialize language system
from MGBMUSIC.core.lang import Language
lang = Language()

# Initialize Telegram and YouTube utilities
from MGBMUSIC.core.telegram import Telegram
from MGBMUSIC.core.youtube import YouTube
tg = Telegram()
yt = YouTube()

# Initialize preload manager for background track downloading
from MGBMUSIC.core.preload import PreloadManager
preload = PreloadManager()

# Initialize queue manager
from MGBMUSIC.helpers import Queue
queue = Queue()

# Initialize preload manager for next-track downloading
from MGBMUSIC.helpers._preload import PreloadManager
preload = PreloadManager()

# Initialize call handler
from MGBMUSIC.core.calls import TgCall
tune = TgCall()


def html_button(text: str, url: str = None, callback_data: str = None) -> str:
    """Return an HTML button element (<button> / <a href>) for UI & HTML outputs."""
    if url:
        return f'<a href="{url}"><button type="button">{text}</button></a>'
    if callback_data:
        return f'<button type="button" data-callback="{callback_data}">{text}</button>'
    return f'<button type="button">{text}</button>'


MGBMUSIC_HTML_BUTTONS = [
    html_button("MGBMUSIC Channel", url="https://t.me/MGB_SUPPROT_GROUP"),
    html_button("MGB NOT FREE CODER", url="https://t.me/mgb_not_free_coder"),
]


async def stop() -> None:
    """
    Gracefully shutdown the bot and all its components.
    
    This function:
    - Cancels all running background tasks
    - Closes bot and userbot connections
    - Closes database connection
    - Logs shutdown completion
    """
    logger.info("🛑 Stopping bot...")
    
    # Cancel all background tasks
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            # Expected when cancelling tasks - suppress the error
            pass
        except Exception:
            pass
    
    # Close all connections
    await app.exit()
    await userbot.exit()
    await db.close()
    
    logger.info("✅ Bot stopped successfully.\n")
    
