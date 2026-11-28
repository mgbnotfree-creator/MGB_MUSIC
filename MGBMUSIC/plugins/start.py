# ==========================================================
# Copyright (c) 2026 MGB NOT FREE CODER
# All Rights Reserved.
#
# Project      : MGB API Telegram Music Bot
# Powered By   : ❖ MGB NOT FREE ❖
# Type         : API Based Telegram Music Bot
#
# Bot          : @Yasmeen_api_bot
# Channel      : https://t.me/MGB_SUPPROT_GROUP
# Group        : https://t.me/mgb_not_free_coder
# GitHub       : https://github.com/mgbnotfree-creator/MGBMusic
# ==========================================================

import asyncio
import random
import re
import aiohttp
from pyrogram import enums, errors, filters, types
from pyrogram import StopPropagation

from MGBMUSIC import app, config, db, lang, logger
from MGBMUSIC.helpers import buttons, utils

# ----------------------------------------------------------
# ✨ ANIMATION & MIDDLE FULL-SCREEN EFFECT CONFIGURATION ✨
# ----------------------------------------------------------
RAIN_EMOJIS = ["❤️", "🔥", "🥰", "❤️‍🔥", "💥", "🤩", "⚡️", "💯", "✨", "🏆"]

MIDDLE_EFFECT_IDS = [
    "5159385139981059251",  # ❤️ Hearts Rain (Middle Screen)
    "5104841245755180586",  # 🔥 Fire Explosion (Middle Screen)
    "5046509860389126442",  # 🎉 Party Popper (Middle Screen)
]

_LOAD_FRAMES = [
    "⏳ <b>लोड़ हो रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■□□□□□□□□□</code>",
    "⌛ <b>डेटा कनेक्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■□□□□□□</code>",
    "⏳ <b>इफ़ेक्ट्स स्टार्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■□□□</code>",
    "✨ <b>बॉट तैयार है!</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■■■■</code>",
]


async def _middle_screen_effect(chat_id: int):
    """स्क्रीन के बिल्कुल बीच (Middle) में दिलों/आग का फुल-स्क्रीन एनिमेटेड इमोजी चलाता है।"""
    if not config.BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "✨",
        "message_effect_id": random.choice(MIDDLE_EFFECT_IDS),
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if data.get("ok"):
                    msg_id = data["result"]["message_id"]
                    await asyncio.sleep(2.2)
                    try:
                        await app.delete_messages(chat_id, msg_id)
                    except Exception:
                        pass
    except Exception:
        pass


async def _emoji_rain(message: types.Message):
    emoji = random.choice(RAIN_EMOJIS)
    try:
        await app.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji=emoji, big=True)
    except Exception:
        pass


async def _loading_animation(message: types.Message):
    try:
        msg = await message.reply_text(_LOAD_FRAMES[0])
        for frame in _LOAD_FRAMES[1:]:
            await asyncio.sleep(0.3)
            try:
                await msg.edit_text(frame)
            except Exception:
                break
        await asyncio.sleep(0.3)
        await msg.delete()
    except Exception:
        pass


# ----------------------------------------------------------
# 🎨 HTML BUTTONS + PHOTO SENDER (NO CUT IMAGE, WORKING HELP) 🎨
# ----------------------------------------------------------

def get_random_start_img():
    """Pick ONE random image URL from config.START_IMG."""
    if not config.START_IMG:
        return "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"
    img_list = str(config.START_IMG).split()
    return random.choice(img_list) if img_list else "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"


_BTN_RE = re.compile(r'<tg-button\s+([^>]+)>(.*?)</tg-button>', re.IGNORECASE | re.DOTALL)
_ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def _parse_tg_buttons(html_rows: str):
    """<tg-button> टैग्स को असली रंगीन inline_keyboard में बदलता है।"""
    kb = []
    for line in html_rows.strip().splitlines():
        matches = list(_BTN_RE.finditer(line))
        if not matches:
            continue
        row = []
        for m in matches:
            attrs = dict(_ATTR_RE.findall(m.group(1)))
            label = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            btn = {"text": label}
            if "url" in attrs:
                btn["url"] = attrs["url"]
            elif "data" in attrs:
                btn["callback_data"] = attrs["data"]
            if "style" in attrs:
                btn["style"] = attrs["style"]
            row.append(btn)
        if row:
            kb.append(row)
    return {"inline_keyboard": kb} if kb else None


def _markup_to_tg_html(markup) -> str:
    """Pyrogram InlineKeyboardMarkup को <tg-button> HTML टैग्स में बदलता है।"""
    if isinstance(markup, str):
        return markup
    rows = getattr(markup, "inline_keyboard", None)
    if not isinstance(rows, list):
        return ""
    lines = []
    for row in rows:
        tags = []
        for btn in row:
            text = getattr(btn, "text", "")
            cb = getattr(btn, "callback_data", None)
            url = getattr(btn, "url", None)
            if "close" in str(cb or "").lower() or "back" in str(cb or "").lower():
                style = "danger"
            else:
                style = "primary"
            if url:
                tags.append(f'<tg-button type="url" style="{style}" url="{url}">{text}</tg-button>')
            elif cb:
                tags.append(f'<tg-button type="callback" style="{style}" data="{cb}">{text}</tg-button>')
        if tags:
            lines.append(" ".join(tags))
    return "\n".join(lines)


async def _send_html_photo_card(chat_id: int, photo_url: str, text: str, html_buttons: str):
    """फुल इमेज + HTML रंगीन बटन्स के साथ कार्ड भेजता है।"""
    if not config.BOT_TOKEN:
        return None
    kb = _parse_tg_buttons(html_buttons)
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": text,
        "parse_mode": "HTML",
    }
    if kb:
        payload["reply_markup"] = kb

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]
    except Exception:
        pass
    return None


async def _send_rich_start(chat_id: int, photo_url: str, text: str):
    html_btns = (
        f'<tg-button type="url" style="success" url="https://t.me/{app.username}?startgroup=true">➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ</tg-button>\n'
        f'<tg-button type="callback" style="primary" data="mgb_help">📚 Hᴇʟᴘ</tg-button> '
        f'<tg-button type="url" style="danger" url="https://t.me/MGB_NOT_FREE_1">👑 Oᴡɴᴇʀ</tg-button>\n'
        f'<tg-button type="url" style="primary" url="https://t.me/mgb_not_free_coder">💬 Sᴜᴘᴘᴏʀᴛ</tg-button> '
        f'<tg-button type="url" style="primary" url="https://t.me/MGB_SUPPROT_GROUP">📢 Cʜᴀɴɴᴇʟ</tg-button>'
    )
    return await _send_html_photo_card(chat_id, photo_url, text, html_btns)


async def _send_rich_help(chat_id: int, photo_url: str, text: str, html_buttons):
    tg_html = _markup_to_tg_html(html_buttons)
    return await _send_html_photo_card(chat_id, photo_url, text, tg_html)


# ----------------------------------------------------------
# 🚀 SUPER OVERRIDES (FIXES HELP MENU & CLOSE BUTTONS) 🚀
# ----------------------------------------------------------

@app.on_callback_query(filters.regex(r"^start$") & ~app.bl_users, group=-2)
@lang.language()
async def rich_start_cb(_, query: types.CallbackQuery):
    """जब आप '❌ CLOSE' दबाएंगे, तो यह नया कलरफुल स्टार्ट मेन्यू लाएगा!"""
    await query.answer()
    _text = (
        query.lang["start_pm"].format(query.from_user.first_name, app.name)
        if query.message.chat.type == enums.ChatType.PRIVATE
        else query.lang["start_gp"].format(app.name)
    )
    try:
        await query.message.delete()
    except Exception:
        pass

    random_pic = get_random_start_img()
    await _send_rich_start(query.message.chat.id, random_pic, _text)
    raise StopPropagation


@app.on_callback_query(filters.regex(r"^(mgb_help|help($|_)|settings_back_helper$)") & ~app.bl_users, group=-2)
@lang.language()
async def rich_help_categories_cb(_, query: types.CallbackQuery):
    """यह हेल्प मेन्यू और उसके सभी अंदरूनी बटन्स को HTML में लोड करेगा!"""
    data = query.data
    category = data.replace("help_", "") if data.startswith("help_") else "main"

    if category == "langs":
        return

    await query.answer()

    if category == "main" or data in ("mgb_help", "help", "settings_back_helper"):
        help_text = (
            f"<b>✨ {app.name} - HELP MENU ✨</b>\n\n"
            "• <b>/play [Song Name / URL]</b> - Play music in voice chat\n"
            "• <b>/vplay [Video Name / URL]</b> - Play video in voice chat\n"
            "• <b>/skip</b> - Skip to the next song\n"
            "• <b>/pause</b> - Pause the music stream\n"
            "• <b>/resume</b> - Resume the music stream\n"
            "• <b>/stop</b> - Stop music and clear queue\n"
            "• <b>/settings</b> - Configure bot settings (Admin only)"
        )
        html_buttons = buttons.help_markup(query.lang)
    else:
        raw_text = buttons.help_text(query.lang, category) or query.lang.get(f"help_{category}") or "Help content not found."
        help_text = str(raw_text).replace("<", "&lt;").replace(">", "&gt;")
        html_buttons = buttons.help_markup(query.lang, back=True)

    try:
        await query.message.delete()
    except Exception:
        pass

    random_pic = get_random_start_img()
    await _send_rich_help(query.message.chat.id, random_pic, help_text, html_buttons)
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

    help_text = (
        f"<b>✨ {app.name} - HELP MENU ✨</b>\n\n"
        "• <b>/play [Song Name / URL]</b> - Play music in voice chat\n"
        "• <b>/vplay [Video Name / URL]</b> - Play video in voice chat\n"
        "• <b>/skip</b> - Skip to the next song\n"
        "• <b>/pause</b> - Pause the music stream\n"
        "• <b>/resume</b> - Resume the music stream\n"
        "• <b>/stop</b> - Stop music and clear queue\n"
        "• <b>/settings</b> - Configure bot settings (Admin only)"
    )
    html_buttons = buttons.help_markup(m.lang)
    sent_data = None
    try:
        random_pic = get_random_start_img()
        sent_data = await _send_rich_help(m.chat.id, random_pic, help_text, html_buttons)
    except Exception:
        pass
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
        asyncio.create_task(_middle_screen_effect(message.chat.id))
        await _emoji_rain(message)
        await _loading_animation(message)

    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private else message.lang["start_gp"].format(app.name)
    )

    random_pic = get_random_start_img()
    sent_data = None
    try:
        sent_data = await _send_rich_start(message.chat.id, random_pic, _text)
    except Exception:
        pass

    if not sent_data:
        try:
            key = buttons.start_key(message.lang, private)
            sent_msg = await message.reply_photo(photo=random_pic, caption=_text, reply_markup=key)
            if sent_msg:
                sent_data = {"message_id": sent_msg.id}
        except Exception:
            pass

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
    sent = await utils.safe_text(
        message,
        message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(message.lang, admin_only, force_admin, "en", message.chat.id),
        quote=True,
    )
    if sent:
        try:
            await app.send_reaction(message.chat.id, sent.id, "❤️")
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
