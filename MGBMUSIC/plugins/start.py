# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================

import json
import os
import re
import aiohttp
from pyrogram import enums, errors, filters, types

from MGBMUSIC import app, config, db, lang
from MGBMUSIC.helpers import buttons, utils

_BTN_RE = re.compile(
    r'<tg-button\s+([^>]+)>(.*?)</tg-button>',
    re.IGNORECASE | re.DOTALL,
)
_ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def parse_html_buttons(html_text: str):
    """<tg-button ...> टैग्स को पार्स करके (clean_text, inline_keyboard) बनाता है।"""
    rows = []
    clean_lines = []

    for line in html_text.splitlines():
        matches = list(_BTN_RE.finditer(line))
        if matches:
            row = []
            for m in matches:
                attrs = dict(_ATTR_RE.findall(m.group(1)))
                label = re.sub(r"<[^>]+>", "", m.group(2)).strip()
                btn = {"text": label}

                if "url" in attrs:
                    btn["url"] = attrs["url"]
                elif "callback" in attrs:
                    btn["callback_data"] = attrs["callback"]
                elif "copy_text" in attrs:
                    btn["copy_text"] = {"text": attrs["copy_text"]}

                if "style" in attrs:
                    btn["style"] = attrs["style"]  # primary | success | danger
                if "emoji_id" in attrs:
                    btn["icon_custom_emoji_id"] = attrs["emoji_id"]

                row.append(btn)
            if row:
                rows.append(row)
            rem = _BTN_RE.sub("", line).strip()
            if rem:
                clean_lines.append(rem)
        else:
            clean_lines.append(line)

    return "\n".join(clean_lines).strip(), rows


def markup_to_html_buttons(markup, first_style: str = "success") -> str:
    """Pyrogram InlineKeyboardMarkup को <tg-button> HTML टैग्स में बदलता है।"""
    if not markup:
        return ""
    rows = getattr(markup, "inline_keyboard", None)
    if not isinstance(rows, list):
        return ""

    lines = []
    for r_idx, row in enumerate(rows):
        tags = []
        for b_idx, btn in enumerate(row):
            label = re.sub(r"<[^>]+>", "", getattr(btn, "text", "")).strip()
            if r_idx == 0 and b_idx == 0:
                style = first_style
            elif "close" in str(getattr(btn, "callback_data", "")).lower():
                style = "danger"
            else:
                style = "primary"

            if getattr(btn, "url", None):
                tags.append(f'<tg-button url="{btn.url}" style="{style}">{label}</tg-button>')
            elif getattr(btn, "callback_data", None):
                tags.append(f'<tg-button callback="{btn.callback_data}" style="{style}">{label}</tg-button>')
        if tags:
            lines.append(" ".join(tags))
    return "\n".join(lines)


async def sendRichMessage(
    message: types.Message,
    html_text: str,
    photo=None,
    quote: bool = True,
    fallback_markup=None,
):
    """100% HTML <tg-button> सपोर्ट के साथ मैसेज या फोटो भेजता है।"""
    token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    clean_text, keyboard = parse_html_buttons(html_text)

    if token:
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if photo:
                    first_photo = str(photo).split()[0] if isinstance(photo, str) else photo
                    url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    payload = {
                        "chat_id": message.chat.id,
                        "photo": first_photo,
                        "caption": clean_text,
                        "parse_mode": "HTML",
                    }
                else:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {
                        "chat_id": message.chat.id,
                        "text": clean_text,
                        "parse_mode": "HTML",
                        "link_preview_options": {"is_disabled": True},
                    }

                if keyboard:
                    payload["reply_markup"] = {"inline_keyboard": keyboard}

                if quote:
                    payload["reply_parameters"] = {
                        "message_id": message.id,
                        "allow_sending_without_reply": True,
                    }

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
            caption=clean_text,
            reply_markup=fallback_markup,
            quote=quote,
        )
    return await utils.reply(
        message,
        text=clean_text,
        reply_markup=fallback_markup,
        quote=quote,
    )


def _build_start_html(base_text: str, private: bool) -> str:
    """Start मैसेज के साथ सीधे 100% HTML <tg-button> जोड़ता है।"""
    bot_user = app.username
    owner_url = f"https://t.me/{config.OWNER_ID}" if str(getattr(config, "OWNER_ID", "")).startswith("@") else "https://t.me/MGB_NOT_FREE_1"
    channel_url = getattr(config, "SUPPORT_CHANNEL", None) or "https://t.me/MGB_SUPPROT_GROUP"
    support_url = getattr(config, "SUPPORT_CHAT", None) or "https://t.me/mgb_not_free_coder"

    if private:
        html_btns = (
            f'<tg-button url="https://t.me/{bot_user}?startgroup=true" style="success">➕ ᴀᴅᴅ ϻє ᴛσ ʏσυʀ ɢʀσυᴘ</tg-button>\n'
            f'<tg-button url="{owner_url}" style="danger">👑 σᴡηєʀ</tg-button> '
            f'<tg-button callback="settings_back_helper" style="primary">📚 ʜєʟᴘ</tg-button>\n'
            f'<tg-button url="{channel_url}" style="primary">📢 ᴄʜᴧηηєʟ</tg-button> '
            f'<tg-button url="{support_url}" style="primary">💬 sυᴘᴘσʀᴛ</tg-button>'
        )
    else:
        html_btns = (
            f'<tg-button url="https://t.me/{bot_user}?start=help" style="success">📚 ʜєʟᴘ & ᴄσϻϻᴧηᴅs</tg-button>\n'
            f'<tg-button url="{channel_url}" style="primary">📢 ᴄʜᴧηηєʟ</tg-button> '
            f'<tg-button url="{support_url}" style="primary">💬 sυᴘᴘσʀᴛ</tg-button>'
        )
    return f"{base_text}\n\n{html_btns}"


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with HTML buttons."""
    try:
        await m.delete()
    except Exception:
        pass

    fb_markup = buttons.help_markup(m.lang)
    html_text = f"{m.lang['help_menu']}\n\n{markup_to_html_buttons(fb_markup, first_style='primary')}"

    try:
        await sendRichMessage(
            m,
            html_text=html_text,
            photo=config.START_IMG,
            quote=True,
            fallback_markup=fb_markup,
        )
    except Exception:
        await sendRichMessage(
            m,
            html_text=html_text,
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
    html_payload = _build_start_html(_text, private)

    try:
        await sendRichMessage(
            message,
            html_text=html_payload,
            photo=config.START_IMG,
            quote=not private,
            fallback_markup=fb_key,
        )
    except errors.ChatSendPhotosForbidden:
        try:
            await sendRichMessage(
                message,
                html_text=html_payload,
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
    html_text = f"{message.lang['start_settings'].format(message.chat.title)}\n\n{markup_to_html_buttons(fb_markup)}"

    await sendRichMessage(
        message,
        html_text=html_text,
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
            
