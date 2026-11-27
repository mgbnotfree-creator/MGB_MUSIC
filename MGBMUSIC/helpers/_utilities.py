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
import re
from urllib.parse import urlparse

from pyrogram import enums, errors, types
from MGBMUSIC import app, config, db


def _html_btn(text: str, **kwargs) -> types.InlineKeyboardButton:
    """HTML & Custom Emoji Button Helper for MGBMUSIC"""
    clean_text = re.sub(r"<[^>]+>", "", str(text))
    kwargs.setdefault("style", enums.ButtonStyle.PRIMARY)
    return types.InlineKeyboardButton(text=clean_text, **kwargs)


class Utilities:
    def __init__(self):
        pass

    def format_eta(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d} min"
        else:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d} h"

    def format_size(self, bytes: int) -> str:
        if bytes >= 1024**3:
            return f"{bytes / 1024 ** 3:.2f} GB"
        elif bytes >= 1024**2:
            return f"{bytes / 1024 ** 2:.2f} MB"
        else:
            return f"{bytes / 1024:.2f} KB"

    def format_duration(self, seconds: int) -> str:
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"

    def to_seconds(self, time: str) -> int:
        parts = [int(p) for p in time.strip().split(":")]
        return sum(value * 60**i for i, value in enumerate(reversed(parts)))

    async def extract_user(self, msg: types.Message) -> types.User | None:
        if msg.reply_to_message:
            return msg.reply_to_message.from_user

        if msg.entities:
            for e in msg.entities:
                if e.type == enums.MessageEntityType.TEXT_MENTION:
                    return e.user

        if msg.text:
            try:
                if m := re.search(r"@(\w{5,32})", msg.text):
                    return await app.get_users(m.group(0))
                if m := re.search(r"\b\d{6,15}\b", msg.text):
                    return await app.get_users(int(m.group(0)))
            except Exception:
                pass

        return None

    async def play_log(
        self,
        m: types.Message,
        title: str,
        duration: str,
    ) -> None:
        if m.chat.id == app.logger:
            return
        _text = m.lang["play_log"].format(
            app.name,
            m.chat.id,
            m.chat.title,
            m.from_user.id,
            m.from_user.mention,
            m.link,
            title,
            duration,
        )
        await app.send_message(chat_id=app.logger, text=_text)

    async def autoplay_log(
        self,
        chat,
        user,
        enabled: bool,
        source: str = "command",
        target_chat_id: int | None = None,
        link: str | None = None,
    ) -> None:
        try:
            if not await db.is_logger():
                return
            if chat.id == app.logger:
                return
            state = "ON ✅" if enabled else "OFF ⏹"
            _text = (
                f"<blockquote>🔁  {app.name} ᴀυᴛσᴘʟᴧʏ ʟσɢ\n\n"
                f"🏠  ᴄʜᴧᴛ: <code>{chat.id}</code>  ┊  {chat.title}\n"
                f"👤  υsєʀ: <code>{user.id}</code>  ┊  {user.mention}\n"
            )
            if target_chat_id and target_chat_id != chat.id:
                _text += f"📡  ᴛᴧʀɢєᴛ ᴄʜᴧηηєʟ: <code>{target_chat_id}</code>\n"
            if link:
                _text += f"🔗  {link}\n"
            _text += (
                f"\n⚙️  ᴀυᴛσᴘʟᴧʏ: <b>{state}</b>\n"
                f"🕹  ᴠɪᴧ: {source}</blockquote>"
            )
            await app.send_message(chat_id=app.logger, text=_text)
        except Exception:
            pass

    async def send_log(self, m: types.Message) -> None:
        await app.send_message(
            chat_id=app.logger,
            text=m.lang["log_user"].format(
                m.from_user.id,
                f"@{m.from_user.username}",
                m.from_user.mention,
            ),
        )

    def media_kind(self, media) -> str:
        from config import media_kind
        return media_kind(media)

    def input_media(self, media, caption: str | None = None, spoiler: bool = False):
        kind = self.media_kind(media)
        if kind == "animation":
            return types.InputMediaAnimation(media=media, caption=caption, has_spoiler=spoiler)
        if kind == "video":
            return types.InputMediaVideo(media=media, caption=caption, has_spoiler=spoiler)
        if kind == "svg":
            return types.InputMediaDocument(media=media, caption=caption)
        return types.InputMediaPhoto(media=media, caption=caption, has_spoiler=spoiler)

    async def send_media(
        self,
        chat_id,
        media,
        caption: str | None = None,
        reply_markup=None,
        reply_parameters=None,
        spoiler: bool = False,
        **kwargs,
    ) -> types.Message:
        if spoiler:
            kwargs["has_spoiler"] = True
        kind = self.media_kind(media)
        if kind == "animation":
            return await app.send_animation(
                chat_id=chat_id,
                animation=media,
                caption=caption,
                reply_markup=reply_markup,
                reply_parameters=reply_parameters,
                **kwargs,
            )
        if kind == "svg":
            return await app.send_document(
                chat_id=chat_id,
                document=media,
                caption=caption,
                reply_markup=reply_markup,
                reply_parameters=reply_parameters,
            )
        if kind == "video":
            return await app.send_video(
                chat_id=chat_id,
                video=media,
                caption=caption,
                reply_markup=reply_markup,
                reply_parameters=reply_parameters,
                **kwargs,
            )
        return await app.send_photo(
            chat_id=chat_id,
            photo=media,
            caption=caption,
            reply_markup=reply_markup,
            reply_parameters=reply_parameters,
            **kwargs,
        )

    def close_markup(self, chat_id: int) -> types.InlineKeyboardMarkup:
        return types.InlineKeyboardMarkup([[
            _html_btn(
                text="<b>• ᴄʟσsє •</b>",
                callback_data=f"controls close {chat_id}",
                style=enums.ButtonStyle.DANGER,
            )
        ]])

    async def reply(
        self,
        message: types.Message,
        *,
        text: str | None = None,
        photo=None,
        caption: str | None = None,
        quote: bool = True,
        reply_markup=None,
        **kwargs,
    ) -> types.Message | None:
        reply_parameters = types.ReplyParameters(message_id=message.id) if quote else None
        if photo is not None:
            return await self.send_media(
                chat_id=message.chat.id,
                media=photo,
                caption=caption,
                reply_markup=reply_markup,
                reply_parameters=reply_parameters,
                **kwargs,
            )
        return await app.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=reply_markup,
            reply_parameters=reply_parameters,
            **kwargs,
        )

    async def safe_text(
        self,
        message: types.Message,
        text: str,
        *,
        reply_markup=None,
        quote: bool | None = True,
    ) -> types.Message | None:
        if not message:
            return None
        try:
            return await self.reply(
                message,
                text=text,
                reply_markup=reply_markup,
                quote=bool(quote),
            )
        except (errors.ChatSendPlainForbidden, errors.ChatWriteForbidden):
            fallback_photo = getattr(config, "START_IMG", None)
            if not fallback_photo:
                return None
            try:
                return await self.reply(
                    message,
                    photo=fallback_photo,
                    caption=text,
                    reply_markup=reply_markup,
                    quote=bool(quote),
                )
            except errors.RPCError:
                return None
        except errors.RPCError:
            return None

    async def safe_edit(
        self,
        message: types.Message | None,
        text: str,
        *,
        reply_markup=None,
    ) -> bool:
        if not message:
            return False
        try:
            if message.text is not None:
                await message.edit_text(text=text, reply_markup=reply_markup)
            else:
                await message.edit_caption(caption=text, reply_markup=reply_markup)
            return True
        except errors.RPCError:
            return False
