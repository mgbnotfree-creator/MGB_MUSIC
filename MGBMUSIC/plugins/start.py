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
# ==========================================================

import asyncio
import html
import os
import random
import aiohttp
from pyrogram import StopPropagation, enums, filters, types

try:
    from MGBMUSIC import app, config, db, lang
    from MGBMUSIC.helpers import buttons, utils
except ImportError:
    from ArtistMusic import app, config, db, lang
    from ArtistMusic.helpers import buttons, utils

# ----------------------------------------------------------
# ✨ DOUBLE ANIMATION & EFFECT CONFIGURATION ✨
# ----------------------------------------------------------
RAIN_EMOJIS = ["❤️", "🔥", "🥰", "❤️‍🔥", "💥", "🤩", "⚡️", "💯", "✨", "🏆"]

EFFECT_IDS = [
    "5104841245755180586",  # 🔥 Fire
    "5046509860389126442",  # 🎉 Celebration
    "5159385139981059251",  # ❤️ Hearts
]

_LOAD_FRAMES = [
    "⏳ <b>लोड हो रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■□□□□□□□□□</code>",
    "⌛ <b>डेटा कनेक्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■□□□□□□</code>",
    "⏳ <b>इफेक्ट्स स्टार्ट कर रहा है...</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■□□□</code>",
    "✨ <b>बॉट तैयार है!</b>\n<blockquote>⚡ MGB NOT FREE CODER ⚡</blockquote>\n<code>■■■■■■■■■■</code>",
]


async def _emoji_burst(chat_id: int, message_id: int, emoji: str):
    try:
        await app.send_reaction(
            chat_id=chat_id,
            message_id=message_id,
            emoji=emoji,
            big=True,
        )
    except Exception:
        pass


async def _loading_animation(message: types.Message):
    msg = None
    try:
        try:
            msg = await message.reply_text(
                _LOAD_FRAMES[0],
                parse_mode=enums.ParseMode.HTML,
                effect_id=int(random.choice(EFFECT_IDS)),
            )
        except Exception:
            msg = await message.reply_text(
                _LOAD_FRAMES[0],
                parse_mode=enums.ParseMode.HTML,
            )

        for frame in _LOAD_FRAMES[1:]:
            await asyncio.sleep(0.35)
            try:
                await msg.edit_text(frame, parse_mode=enums.ParseMode.HTML)
            except Exception:
                break

        await asyncio.sleep(0.35)
        await msg.delete()
    except Exception:
        if msg:
            try:
                await msg.delete()
            except Exception:
                pass


async def _double_animation(message: types.Message):
    e1 = random.choice(["❤️", "🔥", "❤️‍🔥"])
    e2 = random.choice(["🔥", "🎉", "💥", "🤩", "⚡️"])

    async def _two_reactions():
        await _emoji_burst(message.chat.id, message.id, e1)
        await asyncio.sleep(0.75)
        await _emoji_burst(message.chat.id, message.id, e2)

    await asyncio.gather(
        _two_reactions(),
        _loading_animation(message),
    )


# ----------------------------------------------------------
# 🎨 SMART RICH MESSAGE API + COLORED HTML BUTTONS FALLBACK 🎨
# ----------------------------------------------------------
def get_random_start_img():
    raw = getattr(config, "START_IMG", None)
    if not raw:
        return "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"
    img_list = str(raw).split()
    if not img_list:
        return "https://i.ibb.co/8nyBbj1G/uploaded-image.jpg"
    return random.choice(img_list)


def _markup_to_tg_html(markup) -> str:
    if not markup:
        return ""
    if isinstance(markup, str):
        return markup

    rows = (
        markup.get("inline_keyboard", [])
        if isinstance(markup, dict)
        else getattr(markup, "inline_keyboard", [])
    )
    if not isinstance(rows, list):
        return ""

    out = []
    for row in rows:
        btns_html = []
        for btn in row:
            if isinstance(btn, dict):
                text = html.escape(str(btn.get("text", "")))
                url = btn.get("url")
                cb = btn.get("callback_data")
                st = str(btn.get("style", "primary")).lower()
            else:
                text = html.escape(str(getattr(btn, "text", "")))
                url = getattr(btn, "url", None)
                cb = getattr(btn, "callback_data", None)
                raw_st = getattr(btn, "style", None)
                st = (
                    str(getattr(raw_st, "value", None) or getattr(raw_st, "name", None) or raw_st).lower()
                    if raw_st
                    else "primary"
                )

            if "danger" in st:
                style = "danger"
            elif "success" in st:
                style = "success"
            else:
                style = "primary"

            if url:
                btns_html.append(
                    f'<tg-button type="url" style="{style}" url="{html.escape(str(url))}">{text}</tg-button>'
                )
            elif cb:
                btns_html.append(
                    f'<tg-button type="callback" style="{style}" data="{html.escape(str(cb))}">{text}</tg-button>'
                )
        if btns_html:
            out.append(f'<tg-button-row align="center">{"".join(btns_html)}</tg-button-row>')
    return "".join(out)


async def _send_rich_start(chat_id: int, photo_url: str, text: str):
    bot_token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    if not bot_token:
        return None

    support_url = getattr(config, "SUPPORT_CHAT", None) or "https://t.me/mgb_not_free_coder"
    channel_url = getattr(config, "SUPPORT_CHANNEL", None) or "https://t.me/MGB_SUPPROT_GROUP"
    owner_url = (
        f"tg://openmessage?user_id={config.OWNER_ID}"
        if getattr(config, "OWNER_ID", None)
        else "https://t.me/MGB_NOT_FREE_1"
    )
    safe_text = text.replace("\n", "<br>")

    # 1) Try sendRichMessage first
    rich_body = (
        f"<blockquote>{safe_text}</blockquote><br><br>"
        f'<tg-button-row align="center">'
        f'<tg-button type="url" style="primary" url="https://t.me/{app.username}?startgroup=true">➕ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ</tg-button>'
        f"</tg-button-row>"
        f'<tg-button-row align="center">'
        f'<tg-button type="url" style="primary" url="{owner_url}">👑 Oᴡɴᴇʀ</tg-button>'
        f'<tg-button type="callback" style="success" data="help">📖 Hᴇʟᴘ</tg-button>'
        f"</tg-button-row>"
        f'<tg-button-row align="center">'
        f'<tg-button type="url" style="primary" url="{support_url}">💬 Sᴜᴘᴘᴏʀᴛ</tg-button>'
        f'<tg-button type="url" style="danger" url="{channel_url}">🚀 Cʜᴀɴɴᴇʟ</tg-button>'
        f"</tg-button-row>"
    )
    rich_message = {
        "html": f'<img src="tg://photo?id=player_cover"/><br>{rich_body}',
        "media": [{"id": "player_cover", "media": {"type": "photo", "media": photo_url}}],
    }

    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{bot_token}/sendRichMessage",
                json={"chat_id": chat_id, "rich_message": rich_message},
            ) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]
    except Exception:
        pass

    # 2) Fallback: sendPhoto with exact same stylish font & colours
    kb = {
        "inline_keyboard": [
            [
                {
                    "text": "🎧 Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ",
                    "url": f"https://t.me/{app.username}?startgroup=true",
                    "style": "primary",
                }
            ],
            [
                {"text": "🤵🏻 Oᴡɴᴇʀ", "url": owner_url, "style": "primary"},
                {"text": "🆘 Hᴇʟᴘ", "callback_data": "help", "style": "success"},
            ],
            [
                {"text": "👩🏻‍💻 Sᴜᴘᴘᴏʀᴛ", "url": support_url, "style": "primary"},
                {"text": "🦋 Cʜᴀɴɴᴇʟ", "url": channel_url, "style": "danger"},
            ],
        ]
    }
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": chat_id,
                    "photo": photo_url,
                    "caption": f"<blockquote>{text}</blockquote>",
                    "parse_mode": "HTML",
                    "reply_markup": kb,
                },
            ) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]
    except Exception:
        pass
    return None


async def _send_rich_help(chat_id: int, photo_url: str, text: str, markup):
    bot_token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    if not bot_token:
        return None

    safe_text = text.replace("\n", "<br>")
    html_buttons = _markup_to_tg_html(markup)
    rich_body = f"<blockquote>{safe_text}</blockquote><br><br>{html_buttons}"
    rich_message = {
        "html": f'<img src="tg://photo?id=help_cover"/><br>{rich_body}',
        "media": [{"id": "help_cover", "media": {"type": "photo", "media": photo_url}}],
    }

    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{bot_token}/sendRichMessage",
                json={"chat_id": chat_id, "rich_message": rich_message},
            ) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]
    except Exception:
        pass

    # Guaranteed fallback: sendPhoto with Colored Help Buttons
    rows = (
        markup.get("inline_keyboard", [])
        if isinstance(markup, dict)
        else getattr(markup, "inline_keyboard", [])
    )
    kb_rows = []
    for row in rows or []:
        r = []
        for btn in row:
            if isinstance(btn, dict):
                item = dict(btn)
                item.setdefault("style", "primary")
            else:
                item = {"text": getattr(btn, "text", ""), "style": "primary"}
                if getattr(btn, "url", None):
                    item["url"] = btn.url
                if getattr(btn, "callback_data", None):
                    item["callback_data"] = btn.callback_data
                    if item["callback_data"] in ("start", "help_main"):
                        item["style"] = "success"
            r.append(item)
        if r:
            kb_rows.append(r)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": chat_id,
                    "photo": photo_url,
                    "caption": text,
                    "parse_mode": "HTML",
                    "reply_markup": {"inline_keyboard": kb_rows},
                },
            ) as resp:
                result = await resp.json()
                if result.get("ok"):
                    return result["result"]
    except Exception:
        pass
    return None


# ----------------------------------------------------------
# 🚀 SUPER OVERRIDES (FIXES HELP MENU & CLOSE BUTTONS) 🚀
# ----------------------------------------------------------
@app.on_callback_query(filters.regex(r"^start$") & ~app.bl_users, group=-1)
@lang.language()
async def rich_start_cb(_, query: types.CallbackQuery):
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


@app.on_callback_query(filters.regex(r"^help$|^help_") & ~app.bl_users, group=-1)
@lang.language()
async def rich_help_categories_cb(_, query: types.CallbackQuery):
    data = query.data
    category = data.replace("help_", "") if data.startswith("help_") else "main"

    if category == "langs":
        return

    await query.answer()

    if category in ("main", "man") or data == "help":
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
        help_markup = buttons.help_markup(query.lang)
    else:
        raw_text = (
            buttons.help_text(query.lang, category)
            or query.lang.get(f"help_{category}")
            or "Help content not found."
        )
        help_text = str(raw_text).replace("<", "&lt;").replace(">", "&gt;")
        help_markup = buttons.help_markup(query.lang, back=True)

    try:
        await query.message.delete()
    except Exception:
        pass

    random_pic = get_random_start_img()
    await _send_rich_help(query.message.chat.id, random_pic, help_text, help_markup)
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
    help_markup = buttons.help_markup(m.lang)
    sent_data = None
    try:
        random_pic = get_random_start_img()
        sent_data = await _send_rich_help(m.chat.id, random_pic, help_text, help_markup)
    except Exception:
        pass
    if sent_data and "message_id" in sent_data:
        try:
            await app.send_reaction(m.chat.id, sent_data["message_id"], "👏", big=True)
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
        await _double_animation(message)

    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    sent_data = None
    try:
        random_pic = get_random_start_img()
        sent_data = await _send_rich_start(message.chat.id, random_pic, _text)
    except Exception:
        try:
            key = buttons.start_key(message.lang, private)
            sent_msg = await message.reply_text(text=_text, reply_markup=key)
            if sent_msg:
                sent_data = {"message_id": sent_msg.id}
        except Exception:
            pass

    if private and sent_data and "message_id" in sent_data:
        try:
            selected_emoji = random.choice(["🍓", "❤️‍🔥", "⚡", "🔥", "🥰", "🎉", "💖"])
            await asyncio.sleep(0.4)
            await app.send_reaction(message.chat.id, sent_data["message_id"], selected_emoji, big=True)
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
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, force_admin, "en", message.chat.id
        ),
        quote=True,
    )
    if sent:
        try:
            await app.send_reaction(message.chat.id, sent.id, "❤️", big=True)
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
    
