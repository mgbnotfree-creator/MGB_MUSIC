# ==========================================================
# Copyright (C) 2026 MGB NOT FREE CODER (@MGB_NOT_FREE)
# Project : MGBMUSIC
# Group   : https://t.me/mgb_not_free_coder
# Channel : https://t.me/MGB_SUPPROT_GROUP
# GitHub  : https://github.com/mgbnotfree-creator/MGBMusic
# All rights reserved.
# ==========================================================

import asyncio
import logging
from pyrogram import filters, types
from pyrogram.errors import ChatSendPlainForbidden, ChatWriteForbidden

from MGBMUSIC import tune, app, db, lang
from MGBMUSIC.helpers import can_manage_vc, utils

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _stop(_, m: types.Message):
    try:
        await m.delete()
    except Exception:
        pass
    
    if len(m.command) > 1:
        return
    
    # Check for channel play mode
    is_channel = m.command[0].lower() in ["cend", "cstop"]
    chat_id = m.chat.id
    
    if is_channel:
        channel_id = await db.get_cmode(m.chat.id)
        if channel_id is None:
            return await m.reply_text("Channel play is not enabled. Use /channelplay to enable.")
        chat_id = channel_id
    
    if not await db.get_call(chat_id):
        try:
            return await m.reply_text("Nothing is playing.")
        except (ChatSendPlainForbidden, ChatWriteForbidden):
            logger.warning("Cannot send text in this chat, skipping reply.")
            return
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
            return

    await tune.stop(chat_id)
    try:
        sent_msg = await m.reply_text(
            m.lang["play_stopped"].format(m.from_user.mention),
            reply_markup=utils.close_markup(m.chat.id),
        )
    except (ChatSendPlainForbidden, ChatWriteForbidden):
        logger.warning("Cannot send text in this chat, stream stopped silently.")
        return
    except Exception as e:
        logger.error(f"Failed to send stop confirmation: {e}")
        return
    
    await asyncio.sleep(5)
    try:
        await sent_msg.delete()
    except Exception:
        pass
