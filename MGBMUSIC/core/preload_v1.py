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
import logging
from typing import Dict, Set

logger = logging.getLogger("MGBMUSIC")


class PreloadManager:
    def __init__(self):
        self._tasks: Dict[int, Dict[str, asyncio.Task]] = {}
        self._preloaded: Dict[int, Set[str]] = {}
        self._sem = asyncio.Semaphore(2)

    async def preload_next(self, chat_id: int, media) -> None:
        media_id = getattr(media, "id", None)
        if not media_id:
            return
        if chat_id not in self._tasks:
            self._tasks[chat_id] = {}
        if chat_id not in self._preloaded:
            self._preloaded[chat_id] = set()
        if media_id in self._preloaded[chat_id]:
            logger.debug(f"Track {media_id} already preloaded for chat {chat_id}")
            return
        existing = self._tasks[chat_id].get(media_id)
        if existing and not existing.done():
            return
        task = asyncio.create_task(self._preload_task(chat_id, media))
        self._tasks[chat_id][media_id] = task

    async def _preload_task(self, chat_id: int, media) -> None:
        try:
            from MGBMUSIC import yt
            logger.debug(f"Starting preload for chat {chat_id}: {media.title}")
            video = getattr(media, "video", False)
            if not media.file_path:
                async with self._sem:
                    media.file_path = await yt.download(media.id, video=video)
            if media.file_path:
                self._preloaded.setdefault(chat_id, set()).add(media.id)
                await yt.cache_to_logger(media.id, media.file_path, video=video)
                logger.debug(f"Preload complete for chat {chat_id}: {media.title}")
        except asyncio.CancelledError:
            logger.debug(f"Preload cancelled for chat {chat_id}")
            raise
        except Exception as e:
            logger.error(f"Preload error for chat {chat_id}: {e}")
        finally:
            media_tasks = self._tasks.get(chat_id)
            if media_tasks:
                media_tasks.pop(getattr(media, "id", None), None)
                if not media_tasks:
                    self._tasks.pop(chat_id, None)

    async def cancel_preload(self, chat_id: int) -> None:
        media_tasks = self._tasks.get(chat_id, {})
        if media_tasks:
            active = [task for task in media_tasks.values() if not task.done()]
            for task in active:
                task.cancel()
            if active:
                await asyncio.gather(*active, return_exceptions=True)
            logger.debug(f"Cancelled preload for chat {chat_id}")
        self._preloaded.pop(chat_id, None)
        self._tasks.pop(chat_id, None)

    def is_preloaded(self, chat_id: int, media_id: str) -> bool:
        return media_id in self._preloaded.get(chat_id, set())

    def clear(self, chat_id: int) -> None:
        self._preloaded.pop(chat_id, None)
        self._tasks.pop(chat_id, None)

    async def start_preload(self, chat_id: int, count: int | None = None) -> None:
        try:
            from MGBMUSIC import queue
            from MGBMUSIC.helpers._dataclass import Track
            upcoming = [t for t in queue.get_queue(chat_id)[1:] if isinstance(t, Track)]
            if count:
                upcoming = upcoming[:count]
            for media in upcoming:
                if getattr(media, "is_live", False):
                    continue
                if media.file_path:
                    if not self.is_preloaded(chat_id, media.id):
                        await self.preload_next(chat_id, media)
                    continue
                await self.preload_next(chat_id, media)
        except Exception as e:
            logger.debug(f"Error in start_preload for {chat_id}: {e}")
