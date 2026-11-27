# ==========================================================
# Copyright (c) 2026 MGB NOT FREE CODER
# All Rights Reserved.
#
# Project      : MGB API Telegram Music Bot
# Powered By   : MGB NOT FREE (@MGB_NOT_FREE_1)
# Type         : API Based Telegram Music Bot
#
# Bot          : @Yasmeen_api_bot
# Channel      : https://t.me/MGB_SUPPROT_GROUP
# Group        : https://t.me/mgb_not_free_coder
# GitHub       : https://github.com/mgbnotfree-creator/MGBMusic
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================
import datetime as dt
import html
import json
import re
from functools import wraps
from typing import Optional, Tuple

import aiohttp
from pyrogram.enums import ButtonStyle, ChatMemberStatus, ChatMembersFilter, ChatType
from pyrogram.errors import RPCError
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from MGBMUSIC import app, config, logger

ADMIN_STATUSES = (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
TELEGRAM_SYSTEM_IDS = (777000, 1087968824)


def _html_btn(text: str, **kwargs) -> InlineKeyboardButton:
    clean_text = re.sub(r"<[^>]+>", "", str(text))
    kwargs.setdefault("style", ButtonStyle.PRIMARY)
    return InlineKeyboardButton(text=clean_text, **kwargs)


def mention(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{html.escape(name or "υsєʀ")}</a>'


def esc(text: Optional[str]) -> str:
    return html.escape(text or "")


def parse_time(time_str: str) -> Optional[dt.timedelta]:
    if not time_str or len(time_str) < 2:
        return None
    unit = time_str[-1].lower()
    if unit not in ("s", "m", "h", "d"):
        return None
    try:
        value = int(time_str[:-1])
    except ValueError:
        return None
    if value <= 0:
        return None
    return {
        "s": dt.timedelta(seconds=value),
        "m": dt.timedelta(minutes=value),
        "h": dt.timedelta(hours=value),
        "d": dt.timedelta(days=value),
    }[unit]


async def _resolve_user(client, identifier) -> Optional[User]:
    try:
        if isinstance(identifier, str) and identifier.lstrip("-").isdigit():
            identifier = int(identifier)
        return await client.get_users(identifier)
    except RPCError:
        return None
    except Exception:
        return None


async def _extract(message: Message, client) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        if not target:
            await message.reply_text("<blockquote>ɪ ᴄᴧη'ᴛ υsє ᴛʜᴧᴛ ϻєssᴧɢє (ησ υsєʀ ᴧᴛᴛᴧᴄʜєᴅ).</blockquote>")
            return None, None, None
        rest = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    else:
        if len(message.command) < 2:
            await message.reply_text("<blockquote>sᴘєᴄɪғʏ ᴧ υsєʀ σʀ ʀєᴘʟʏ ᴛσ sσϻєσηє.</blockquote>")
            return None, None, None
        target = await _resolve_user(client, message.command[1])
        if not target:
            await message.reply_text("<blockquote>ɪ ᴄᴧη'ᴛ ғɪηᴅ ᴛʜᴧᴛ υsєʀ.</blockquote>")
            return None, None, None
        rest = message.text.partition(message.command[1])[2].strip() or None

    if target.id == app.id:
        await message.reply_text("<blockquote>ɪ ᴄᴧη'ᴛ ᴅσ ᴛʜᴧᴛ ᴛσ ϻʏsєʟғ 😅</blockquote>")
        return None, None, None
    return target.id, target.first_name, rest


async def extract_user_and_reason(message, client):
    return await _extract(message, client)


async def extract_user_and_title(message, client):
    return await _extract(message, client)


async def is_admin_user(client, chat_id: int, user_id: int) -> bool:
    if user_id in app.sudoers or user_id in TELEGRAM_SYSTEM_IDS:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ADMIN_STATUSES
    except Exception:
        return False


async def is_admin(client, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    if msg.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
        return False
    if not obj.from_user:
        return bool(getattr(msg, "sender_chat", None) and msg.sender_chat.id == msg.chat.id)
    return await is_admin_user(client, msg.chat.id, obj.from_user.id)


async def has_privilege(client, chat_id: int, user_id: int, *privileges: str) -> bool:
    if user_id in app.sudoers:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    if member.status == ChatMemberStatus.OWNER:
        return True
    if member.status == ChatMemberStatus.ADMINISTRATOR and member.privileges:
        return all(getattr(member.privileges, p, False) for p in privileges)
    return False


def admin_required(*privileges: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message: Message, *a, **kw):
            if not message.from_user:
                return await message.reply_text("<blockquote>υηʜɪᴅє ʏσυʀ ᴧᴄᴄσυηᴛ ᴛσ υsє ᴛʜɪs ᴄσϻϻᴧηᴅ.</blockquote>")
            if not await has_privilege(client, message.chat.id, message.from_user.id, *privileges):
                missing = ", ".join(privileges) or "admin"
                return await message.reply_text(
                    f"<blockquote>🚫  <b>ʏσυ ʟᴧᴄᴋ ᴛʜє</b> <code>{missing}</code> <b>ᴘєʀϻɪssɪση.</b></blockquote>"
                )
            return await func(client, message, *a, **kw)

        return wrapper

    return decorator


async def get_group_owner(client, chat_id: int):
    async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        if member.status == ChatMemberStatus.OWNER:
            return member.user
    return None


async def is_owner_or_sudoer(client, chat_id: int, user_id: int):
    owner = await get_group_owner(client, chat_id)
    if user_id in app.sudoers or (owner and user_id == owner.id):
        return True, owner
    return False, owner


async def default_permissions(client, chat_id: int) -> ChatPermissions:
    try:
        chat = await client.get_chat(chat_id)
        if chat.permissions:
            return chat.permissions
    except Exception:
        pass
    try:
        return ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True,
        )
    except TypeError:
        return ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True,
        )


def styled_button(text: str, callback_data: str = None, url: str = None, style: str = None) -> dict:
    clean_text = re.sub(r"<[^>]+>", "", str(text))
    btn = {"text": clean_text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style:
        btn["style"] = style
    return btn


def to_markup(buttons: list[list[dict]]) -> InlineKeyboardMarkup:
    _style_map = {
        "primary": ButtonStyle.PRIMARY,
        "success": ButtonStyle.SUCCESS,
        "danger": ButtonStyle.DANGER,
    }
    return InlineKeyboardMarkup(
        [
            [
                _html_btn(
                    b["text"],
                    callback_data=b.get("callback_data"),
                    url=b.get("url"),
                    style=_style_map.get(b.get("style"), ButtonStyle.PRIMARY),
                )
                for b in row
            ]
            for row in buttons
        ]
    )


async def send_message_colored(chat_id: int, text: str, buttons: list[list[dict]], reply_to: int = None):
    if config.BOT_TOKEN:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": buttons},
        }
        if reply_to:
            payload["reply_parameters"] = {"message_id": reply_to, "allow_sending_without_reply": True}
        try:
            timeout = aiohttp.ClientTimeout(total=20, connect=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage", json=payload
                ) as resp:
                    data = await resp.json()
            if data.get("ok"):
                return True
            logger.warning(f"Colored send failed: {data.get('description')}")
        except Exception as e:
            logger.warning(f"Colored send error: {e}")

    try:
        await app.send_message(chat_id, text, reply_markup=to_markup(buttons), reply_to_message_id=reply_to)
        return True
    except Exception as e:
        logger.warning(f"Fallback send failed: {e}")
        return False


def confirm_buttons(cmd: str) -> list[list[dict]]:
    return [
        [
            styled_button("<b>ʏєs</b>", callback_data=f"{cmd}_yes", style="success"),
            styled_button("<b>ησ</b>", callback_data=f"{cmd}_no", style="danger"),
        ]
    ]
