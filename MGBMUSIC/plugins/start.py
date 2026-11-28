# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================

import os
import re
import aiohttp
from pyrogram import enums, errors, filters, types

from MGBMUSIC import app, config, db, lang
from MGBMUSIC.helpers import buttons, utils


def _markup_to_rich_rows(markup, first_style: str = "success") -> str:
    """Pyrogram InlineKeyboardMarkup को <tg-button-row> + <tg-button> HTML में बदलता है।"""
    if not markup:
        return ""
    if isinstance(markup, str):
        return markup
    rows = getattr(markup, "inline_keyboard", None)
    if not isinstance(rows, list):
        return ""

    html_rows = []
    for r_idx, row in enumerate(rows):
        btns = []
        for b_idx, btn in enumerate(row):
            label = re.sub(r"<[^>]+>", "", getattr(btn, "text", "")).strip()
            cb_data = str(getattr(btn, "callback_data", "") or "")
            if r_idx == 0 and b_idx == 0:
                style = first_style
            elif "close" in cb_data.lower():
                style = "danger"
            else:
                style = "primary"

            if getattr(btn, "url", None):
                btns.append(f'<tg-button type="url" style="{style}" url="{btn.url}">{label}</tg-button>')
            elif cb_data:
                btns.append(f'<tg-button type="callback" style="{style}" data="{cb_data}">{label}</tg-button>')
        if btns:
            html_rows.append(f'<tg-button-row align="center">{"".join(btns)}</tg-button-row>')
    return "".join(html_rows)


async def sendRichMessage(
    message: types.Message,
    text: str,
    html_buttons: str = "",
    photo=None,
    quote: bool = True,
    fallback_markup=None,
):
    """sendRichMessage API (<tg-button-row> + <tg-button>) से HTML बटन भेजता है।"""
    token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    safe_text = text.replace("\n", "<br>")
    rich_body = f"<blockquote>{safe_text}</blockquote><br><br>{html_buttons}" if html_buttons else f"<blockquote>{safe_text}</blockquote>"

    if photo:
        first_photo = str(photo).split()[0] if isinstance(photo, str) else photo
        rich_message = {
            "html": f'<img src="tg://photo?id=rich_cover"/><br>{rich_body}',
            "media": [{"id": "rich_cover", "media": {"type": "photo", "media": first_photo}}],
        }
    else:
        rich_message = {"html": rich_body}

    if token:
        url = f"https://api.telegram.org/bot{token}/sendRichMessage"
        payload = {"chat_id": message.chat.id, "rich_message": rich_message}
        if quote:
            payload["reply_parameters"] = {
                "message_id": message.id,
                "allow_sending_without_reply": True,
            }
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()
                    if data.get("ok"):
                        return data.get("result")
        except Exception:
            pass

    if photo:
        return await utils.reply(
            message,
            photo=photo,
            caption=text,
            reply_markup=fallback_markup,
            quote=quote,
        )
    return await utils.reply(
        message,
        text=text,
        reply_markup=fallback_markup,
        quote=quote,
    )


def _build_start_rich_buttons(private: bool) -> str:
    """Start मैसेज के लिए <tg-button-row> HTML बटन बनाता है।"""
    bot_user = app.username
    owner_url = f"https://t.me/{config.OWNER_ID}" if str(getattr(config, "OWNER_ID", "")).startswith("@") else "https://t.me/MGB_NOT_FREE_1"
    channel_url = getattr(config, "SUPPORT_CHANNEL", None) or "https://t.me/MGB_SUPPROT_GROUP"
    support_url = getattr(config, "SUPPORT_CHAT", None) or "https://t.me/mgb_not_free_coder"

    if private:
        return (
            f'<tg-button-row align="center">'
            f'<tg-button type="url" style="success" url="https://t.me/{bot_user}?startgroup=true">➕ ᴀᴅᴅ ϻє ᴛσ ʏσυʀ ɢʀσυᴘ</tg-button>'
            f'</tg-button-row>'
            f'<tg-button-row align="center">'
            f'<tg-button type="url" style="danger" url="{owner_url}">👑 σᴡηєʀ</tg-button>'
            f'<tg-button type="callback" style="primary" data="settings_back_helper">📚 ʜєʟᴘ</tg-button>'
            f'</tg-button-row>'
            f'<tg-button-row align="center">'
            f'<tg-button type="url" style="primary" url="{channel_url}">📢 ᴄʜᴧηηєʟ</tg-button>'
            f'<tg-button type="url" style="primary" url="{support_url}">💬 sυᴘᴘσʀᴛ</tg-button>'
            f'</tg-button-row>'
        )
    return (
        f'<tg-button-row align="center">'
        f'<tg-button type="url" style="success" url="https://t.me/{bot_user}?start=help">📚 ʜєʟᴘ & ᴄσϻϻᴧηᴅs</tg-button>'
        f'</tg-button-row>'
        f'<tg-button-row align="center">'
        f'<tg-button type="url" style="primary" url="{channel_url}">📢 ᴄʜᴧηηєʟ</tg-button>'
        f'<tg-button type="url" style="primary" url="{support_url}">💬 sυᴘᴘσʀᴛ</tg-button>'
        f'</tg-button-row>'
    )


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with HTML buttons."""
    try:
        await m.delete()
    except Exception:
        pass

    fb_markup = buttons.help_markup(m.lang)
    html_btns = _markup_to_rich_rows(fb_markup, first_style="primary")

    try:
        await sendRichMessage(
            m,
            text=m.lang["help_menu"],
            html_buttons=html_btns,
            photo=config.START_IMG,
            quote=True,
            fallback_markup=fb_markup,
        )
    except Exception:
        await sendRichMessage(
            m,
            text=m.lang["help_menu"],
            html_buttons=html_btns,
            quote=True,
            fallback_markup=fb_markup,
        )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command with 100% HTML <tg-button> tags."""
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

    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )
    fb_key = buttons.start_key(message.lang, private)
    html_btns = _build_start_rich_buttons(private)

    try:
        await sendRichMessage(
            message,
            text=_text,
            html_buttons=html_btns,
            photo=config.START_IMG,
            quote=not private,
            fallback_markup=fb_key,
        )
    except errors.ChatSendPhotosForbidden:
        try:
            await sendRichMessage(
                message,
                text=_text,
                html_buttons=html_btns,
                quote=not private,
                fallback_markup=fb_key,
            )
        except Exception:
            pass
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
    """Handle /playmode or /settings command - show group settings with HTML buttons."""
    try:
        await message.delete()
    except Exception:
        pass

    admin_only = await db.get_play_mode(message.chat.id)
    force_admin = await db.get_force_mode(message.chat.id)
    _language = "en"
    fb_markup = buttons.settings_markup(
        message.lang, admin_only, force_admin, _language, message.chat.id
    )
    html_btns = _markup_to_rich_rows(fb_markup)

    await sendRichMessage(
        message,
        text=message.lang["start_settings"].format(message.chat.title),
        html_buttons=html_btns,
        quote=True,
        fallback_markup=fb_markup,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    """Handle new member events - detect when bot is added to groups."""
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await db.add_chat(message.chat.id)
