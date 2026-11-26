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
import asyncio
from pathlib import Path
from typing import Dict, Set

from MGBMUSIC import logger


class PreloadManager:
    def __init__(self):
        self._preload_tasks: Dict[int, Set[asyncio.Task]] = {}
        self._preloading: Dict[int, Set[str]] = {}

    async def start_preload(self, chat_id: int, count: int = 2) -> None:
        from MGBMUSIC import queue, yt

        upcoming_tracks = queue.peek_next(chat_id, count)
        if not upcoming_tracks:
            return

        if chat_id not in self._preload_tasks:
            self._preload_tasks[chat_id] = set()
        if chat_id not in self._preloading:
            self._preloading[chat_id] = set()

        for track in upcoming_tracks:
            if queue.is_downloaded(track):
                continue

            track_id = getattr(track, 'id', None)
            if not track_id or track_id in self._preloading[chat_id]:
                continue

            self._preloading[chat_id].add(track_id)
            task = asyncio.create_task(self._preload_track(chat_id, track))
            self._preload_tasks[chat_id].add(task)
            task.add_done_callback(lambda t, cid=chat_id: self._cleanup_task(cid, t))

    async def _preload_track(self, chat_id: int, track) -> None:
        from MGBMUSIC import yt

        try:
            track_id = track.id
            is_live = getattr(track, 'is_live', False)
            file_path = await yt.download(
                track_id,
                is_live=is_live,
                video=getattr(track, "video", False),
            )
            if file_path:
                track.file_path = file_path
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"❌ Error preloading track {track.id} for chat {chat_id}: {e}")
        finally:
            if chat_id in self._preloading and track.id in self._preloading[chat_id]:
                self._preloading[chat_id].remove(track.id)

    async def cancel_preload(self, chat_id: int) -> None:
        if chat_id not in self._preload_tasks:
            return

        tasks = self._preload_tasks[chat_id].copy()
        for task in tasks:
            if not task.done():
                task.cancel()

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._preload_tasks[chat_id].clear()
        if chat_id in self._preloading:
            self._preloading[chat_id].clear()

    def _cleanup_task(self, chat_id: int, task: asyncio.Task) -> None:
        if chat_id in self._preload_tasks:
            self._preload_tasks[chat_id].discard(task)
