# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================

import os
import aiohttp
from pyrogram import enums, errors, filters, types

from MGBMUSIC import app, config, db, lang
from MGBMUSIC.helpers import buttons, utils


def _html_kb(markup, first_style: str = "success"):
    """Convert markup into Bot API HTML inline_keyboard with color styles."""
    if markup is None:
        return None
    if isinstance(markup, dict):
        if "inline_keyboard" in markup:
            return markup
        return {"inline_keyboard": markup}

    rows = getattr(markup, "inline_keyboard", None)
    if not isinstance(rows, list):
        return None

    kb = []
    for r_idx, row in enumerate(rows):
        h_row = []
        for b_idx, btn in enumerate(row):
            item = {"text": getattr(btn, "text", "")}
            if getattr(btn, "url", None):
                item["url"] = btn.url
            if getattr(btn, "callback_data", None):
                item["callback_data"] = btn.callback_data
            if getattr(btn, "copy_text", None):
                item["copy_text"] = btn.copy_text

            if r_idx == 0 and b_idx == 0:
                item["style"] = first_style
            elif "close" in str(item.get("callback_data", "")).lower():
                item["style"] = "danger"
            else:
                item["style"] = "primary"

            h_row.append(item)
        kb.append(h_row)
    return {"inline_keyboard": kb}


async def _send_html_reply(message: types.Message, text: str, markup, photo=None, quote: bool = True):
    token = getattr(config, "BOT_TOKEN", None) or os.getenv("BOT_TOKEN")
    kb = _html_kb(markup)

    if token and kb:
        timeout = aiohttp.ClientTimeout(total=15)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if photo:
                    first_photo = str(photo).split()[0] if isinstance(photo, str) else photo
                    url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    payload = {
                        "chat_id": message.chat.id,
                        "photo": first_photo,
                        "caption": text,
                        "parse_mode": "HTML",
                        "reply_markup": kb,
                    }
                else:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {
                        "chat_id": message.chat.id,
                        "text": text,
                        "parse_mode": "HTML",
                        "link_preview_options": {"is_disabled": True},
                        "reply_markup": kb,
                    }

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
            caption=text,
            reply_markup=markup,
            quote=quote,
        )
    return await utils.reply(
        message,
        text=text,
        reply_markup=markup,
        quote=quote,
    )


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with image."""
    try:
        await m.delete()
    except Exception:
        pass

    try:
        await _send_html_reply(
            m,
            text=m.lang["help_menu"],
            markup=buttons.help_markup(m.lang),
            photo=config.START_IMG,
            quote=True,
        )
    except Exception:
        await _send_html_reply(
            m,
            text=m.lang["help_menu"],
            markup=buttons.help_markup(m.lang),
            quote=True,
        )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command."""
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
    key = buttons.start_key(message.lang, private)

    try:
        await _send_html_reply(
            message,
            text=_text,
            markup=key,
            photo=config.START_IMG,
            quote=not private,
        )
    except errors.ChatSendPhotosForbidden:
        try:
            await _send_html_reply(
                message,
                text=_text,
                markup=key,
                quote=not private,
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
    """Handle /playmode or /settings command - show group settings."""
    try:
        await message.delete()
    except Exception:
        pass

    admin_only = await db.get_play_mode(message.chat.id)
    force_admin = await db.get_force_mode(message.chat.id)
    _language = "en"
    await _send_html_reply(
        message,
        text=message.lang["start_settings"].format(message.chat.title),
        markup=buttons.settings_markup(
            message.lang, admin_only, force_admin, _language, message.chat.id
        ),
        quote=True,
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
