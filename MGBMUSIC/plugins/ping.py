# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================
import time
import psutil

from pyrogram import filters, types
from pyrogram.enums import ButtonStyle
from MGBMUSIC import app, tune, boot, config, lang
from MGBMUSIC.helpers import buttons, utils


def _support_markup(text: str) -> types.InlineKeyboardMarkup:
    """Ping message carries only one button: Support."""
    return types.InlineKeyboardMarkup([[
        types.InlineKeyboardButton(text=text, url=config.SUPPORT_CHAT, style=ButtonStyle.PRIMARY)
    ]])


@app.on_message(filters.command(["alive", "ping"]) & ~app.bl_users)
@lang.language()
async def _ping(_, m: types.Message):
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    start = time.time()
    sent = await m.reply_text(m.lang["pinging"])

    def get_time(s): return (lambda r: (f"{r[-1]}, " if r[-1][:-4] != "0" else "") + ":".join(reversed(r[:-1])))(
        [f"{v}{u}" for v, u in zip([s % 60, (s//60) % 60, (s//3600) % 24, s//86400], ["s", "m", "h", "days"])])
    uptime = get_time(int(time.time() - boot))
    latency = round((time.time() - start) * 1000, 2)
    
    # Get system stats
    mem = psutil.virtual_memory()
    ram_usage = f"{round(mem.used / (1024 ** 3), 1)}/{round(mem.total / (1024 ** 3), 1)}GB"
    cpu_percent = psutil.cpu_percent(interval=0.5)
    
    # Get active chats count
    from MGBMUSIC import db
    active_chats = len(await db.get_chats())
    
    caption_text = m.lang["ping_pong"].format(
        latency,
        uptime,
        await tune.ping(),
        ram_usage,
        cpu_percent,
        active_chats,
    )
    
    # Try to send with media, fallback to text if it fails
    try:
        await sent.edit_media(
            media=utils.input_media(config.PING_IMG, caption_text),
            reply_markup=_support_markup(m.lang["support"]),
        )
    except Exception:
        # Fallback to text if media fails
        await sent.edit_text(
            text=caption_text,
            reply_markup=_support_markup(m.lang["support"]),
        )
