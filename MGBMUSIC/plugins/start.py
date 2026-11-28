# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================

import asyncio
import os
import random
from typing import Any, Dict, List, Optional

import aiohttp
from pyrogram import StopPropagation, enums, filters, types

try:
    from MGBMUSIC import app, config, db, lang
    from MGBMUSIC.helpers import buttons, utils
except ImportError:
    from ArtistMusic import app, config, db, lang
    from ArtistMusic.helpers import buttons, utils

# ----------------------------------------------------------
# ✨ ANIMATION & EFFECT CONFIGURATION ✨
# ----------------------------------------------------------
RAIN_EMOJIS = ["❤️", "🔥", "🥰", "❤️‍🔥", "💥", "🤩", "⚡️", "💯", "✨", "🏆"]

_LOAD_FRAMES = [
    "⏳ <b>लोड़ हो रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■□□□□□□□□□</code>",
    "⌛ <b>डेटा कनेक्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■□□□□□□</code>",
    "⏳ <b>इफ़ेक्ट्स स्टार्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■□□□</code>",
    "✨ <b>बॉट तैयार है!</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■■■■</code>",
]


async def _emoji_rain(message: types.Message):
    emoji = random.choice(RAIN_EMOJIS)
    try:
        await app.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=emoji,
            big=True,
        )
    except Exception:
        pass
    await asyncio.sleep(1.0)
    try:
        await app.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=None,
        )
    except Exception:
        pass


async def _loading_animation(message: types.Message):
    try:
        msg = await message.reply_text(_LOAD_FRAMES[0], parse_mode=enums.ParseMode.HTML)
        for frame in _LOAD_FRAMES[1:]:
            await asyncio.sleep(0.3)
            try:
                await msg.edit_text(frame, parse_mode=enums.ParseMode.HTML)
            except Exception:
                break
        await asyncio.sleep(0.3)
        await msg.delete()
    except Exception:
        pass


def get_random_start_img() -> str:
    raw = getattr(config, "START_IMG", None)
    if not raw:
        return "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"
    imgs = str(raw).split()
    return random.choice(imgs) if imgs else "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"


# ----------------------------------------------------------
# 🎨 100% WORKING HTML COLORED BUTTON ENGINE 🎨
# ----------------------------------------------------------
def _hbtn(
    text: str,
    url: Optional[str] = None,
    callback_data: Optional[str] = None,
    style: str = "primary",
) -> Dict[str, Any]:
    btn: Dict[str, Any] = {"text": text, "style": style}
    if url:
        btn["url"] = url
    if callback_data:
        btn["callback_data"] = callback_data
    return btn


def _start_html_rows() -> List[List[Dict[str, Any]]]:
    bot_uname = getattr(app, "username", None) or "Yasmeen_api_bot"
    owner_url = f"tg://openmessage?user_id={getattr(config, 'OWNER_ID', '')}" if getattr(config, "OWNER_ID", None) else "https://t.me/MGB_NOT_FREE_1"
    channel_url = getattr(config, "SUPPORT_CHANNEL", None) or "https://t.me/MGB_SUPPROT_GROUP"
    support_url = getattr(config, "SUPPORT_CHAT", None) or "https://t.me/mgb_not_free_coder"

    return [
        [
            _hbtn(
                "➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ",
                url=f"https://t.me/{bot_uname}?startgroup=true",
                style="primary",
            )
        ],
        [
            _hbtn("👑 Oᴡɴᴇʀ", url=owner_url, style="primary"),
            _hbtn("📖 Hᴇʟᴘ", callback_data="help", style="success"),
        ],
        [
            _hbtn("💬 Sᴜᴘᴘᴏʀᴛ", url=support_url, style="primary"),
            _hbtn("🚀 Cʜᴀɴɴᴇʟ", url=channel_url, style="danger"),
        ],
    ]


def _markup_to_html_rows(markup: Any) -> List[List[Dict[str, Any]]]:
    """Convert any InlineKeyboardMarkup or dict into colored HTML button rows."""
    if markup is None:
        return []
    if isinstance(markup, dict):
        rows = markup.get("inline_keyboard", [])
        return rows if isinstance(rows, list) else []

    rows = getattr(markup, "inline_keyboard", None)
    if not isinstance(rows, list):
        return []

    out: List[List[Dict[str, Any]]] = []
    for row in rows:
        h_row: List[Dict[str, Any]] = []
        for btn in row:
            item: Dict[str, Any] = {"text": getattr(btn, "text", "")}
            if getattr(btn, "url", None):
                item["url"] = btn.url
            if getattr(btn, "callback_data", None):
                item["callback_data"] = btn.callback_data
            if getattr(btn, "copy_text", None):
                item["copy_text"] = btn.copy_text

            st = getattr(btn, "style", None)
            if st:
                st_str = str(getattr(st, "value", None) or getattr(st, "name", None) or st).lower()
                if "danger" in st_str:
                    item["style"] = "danger"
                elif "success" in st_str:
                    item["style"] = "success"
                else:
                    item["style"] = "primary"
            else:
                cb = str(item.get("callback_data", "")).lower()
                if "close" in cb:
                    item["style"] = "danger"
                elif "back" in cb or cb in ("start", "help_main"):
                    item["style"] = "success"
                else:
                    item["style"] = "primary"

            h_row.append(item)
        out.append(h_row)
    return out


async def _send_html_photo(
    chat_id: int,
    photo_url: str,
    caption: str,
    rows: List[List[Dict[str, Any]]],
    reply_to_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    if not token:
        return None

    timeout = aiohttp.ClientTimeout(total=15)
    payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": rows},
    }
    if reply_to_id:
        payload["reply_parameters"] = {
            "message_id": reply_to_id,
            "allow_sending_without_reply": True,
        }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                json=payload,
            ) as resp:
                data = await resp.json()
                if data.get("ok") and isinstance(data.get("result"), dict):
                    return data["result"]
    except Exception:
        pass

    # Text fallback with same colored HTML buttons if photo fails
    text_payload: Dict[str, Any] = {
        "chat_id": chat_id,
        "text": caption,
        "parse_mode": "HTML",
        "link_preview_options": {"is_disabled": True},
        "reply_markup": {"inline_keyboard": rows},
    }
    if reply_to_id:
        text_payload["reply_parameters"] = {
            "message_id": reply_to_id,
            "allow_sending_without_reply": True,
        }

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json=text_payload,
            ) as resp:
                data = await resp.json()
                if data.get("ok") and isinstance(data.get("result"), dict):
                    return data["result"]
    except Exception:
        pass

    return None


# ----------------------------------------------------------
# 🚀 WORKING HELP & START CALLBACK HANDLERS 🚀
# ----------------------------------------------------------
@app.on_callback_query(filters.regex(r"^start$") & ~app.bl_users, group=-1)
@lang.language()
async def rich_start_cb(_, query: types.CallbackQuery):
    await query.answer()
    private = query.message.chat.type == enums.ChatType.PRIVATE
    _text = (
        query.lang["start_pm"].format(query.from_user.first_name, app.name)
        if private
        else query.lang["start_gp"].format(app.name)
    )
    try:
        await query.message.delete()
    except Exception:
        pass

    await _send_html_photo(
        query.message.chat.id,
        get_random_start_img(),
        f"<blockquote>{_text}</blockquote>",
        _start_html_rows(),
    )
    raise StopPropagation


@app.on_callback_query(filters.regex(r"^help$|^help_") & ~app.bl_users, group=-1)
@lang.language()
async def rich_help_categories_cb(_, query: types.CallbackQuery):
    data = query.data
    category = data.replace("help_", "") if data.startswith("help_") else "main"

    if category == "langs":
        return

    await query.answer()

    if category in ("main", "man") or data == "help":
        help_text = query.lang.get("help_menu") or (
            f"<b>✨ {app.name} - HELP MENU ✨</b>\n\n"
            "• <b>/play [Song Name / URL]</b> - Play music in voice chat\n"
            "• <b>/vplay [Video Name / URL]</b> - Play video in voice chat\n"
            "• <b>/skip</b> - Skip to the next song\n"
            "• <b>/pause</b> - Pause the music stream\n"
            "• <b>/resume</b> - Resume the music stream\n"
            "• <b>/stop</b> - Stop music and clear queue\n"
            "• <b>/settings</b> - Configure bot settings"
        )
        rows = _markup_to_html_rows(buttons.help_markup(query.lang))
    else:
        raw_text = (
            buttons.help_text(query.lang, category)
            or query.lang.get(f"help_{category}")
            or "Help content not found."
        )
        help_text = str(raw_text)
        rows = _markup_to_html_rows(buttons.help_markup(query.lang, back=True))

    try:
        await query.message.delete()
    except Exception:
        pass

    await _send_html_photo(
        query.message.chat.id,
        get_random_start_img(),
        help_text,
        rows,
    )
    raise StopPropagation


# ----------------------------------------------------------
# 🤖 BOT COMMANDS (START, HELP, SETTINGS) 🤖
# ----------------------------------------------------------
@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    try:
        await m.delete()
    except Exception:
        pass

    help_text = m.lang.get("help_menu") or (
        f"<b>✨ {app.name} - HELP MENU ✨</b>\n\n"
        "• <b>/play [Song Name / URL]</b> - Play music in voice chat\n"
        "• <b>/vplay [Video Name / URL]</b> - Play video in voice chat\n"
        "• <b>/skip</b> - Skip to the next song\n"
        "• <b>/pause</b> - Pause the music stream\n"
        "• <b>/resume</b> - Resume the music stream\n"
        "• <b>/stop</b> - Stop music and clear queue\n"
        "• <b>/settings</b> - Configure bot settings"
    )
    rows = _markup_to_html_rows(buttons.help_markup(m.lang))
    sent_data = await _send_html_photo(
        m.chat.id,
        get_random_start_img(),
        help_text,
        rows,
    )
    if sent_data and "message_id" in sent_data:
        try:
            await app.send_reaction(m.chat.id, sent_data["message_id"], "👏")
        except Exception:
            pass


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass

    if not message.from_user:
        return
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])
    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE
    if private:
        await _emoji_rain(message)
        await _loading_animation(message)

    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    sent_data = await _send_html_photo(
        message.chat.id,
        get_random_start_img(),
        f"<blockquote>{_text}</blockquote>",
        _start_html_rows(),
        reply_to_id=None if private else message.id,
    )

    if private and sent_data and "message_id" in sent_data:
        try:
            selected_emoji = random.choice(["❤️‍🔥", "⚡", "🔥", "🥰", "🎉", "💖", "🍓"])
            await asyncio.sleep(0.5)
            await app.send_reaction(message.chat.id, sent_data["message_id"], selected_emoji)
        except Exception:
            pass

    if private:
        if await db.is_user(message.from_user.id):
            return
        await utils.send_log(message)
        return await db.add_user(message.from_user.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    try:
        await message.delete()
    except Exception:
        pass

    admin_only = await db.get_play_mode(message.chat.id)
    force_admin = await db.get_force_mode(message.chat.id)
    rows = _markup_to_html_rows(
        buttons.settings_markup(message.lang, admin_only, force_admin, "en", message.chat.id)
    )

    token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    sent_id = None
    if token and rows:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={
                        "chat_id": message.chat.id,
                        "text": message.lang["start_settings"].format(message.chat.title),
                        "parse_mode": "HTML",
                        "reply_markup": {"inline_keyboard": rows},
                    },
                ) as resp:
                    data = await resp.json()
                    if data.get("ok") and isinstance(data.get("result"), dict):
                        sent_id = data["result"]["message_id"]
        except Exception:
            pass

    if sent_id:
        try:
            await app.send_reaction(message.chat.id, sent_id, "❤️")
        except Exception:
            pass


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()
    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await db.add_chat(message.chat.id)
