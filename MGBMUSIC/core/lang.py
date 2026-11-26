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
import json
from functools import wraps
from pathlib import Path

from MGBMUSIC import db, logger

lang_codes = {
    "en": "English 🇬🇧",
    "hi": "Hindi 🇮🇳",
    "te": "Telugu 🇮🇳",
    "ko": "Korean 🇰🇷",
    "my": "Myanmar 🇲🇲",
    "id": "Indonesian 🇮🇩",
    "pt": "Portuguese 🇧🇷",
    "ar": "Arabic 🇸🇦",
    "es": "Spanish 🇪🇸",
    "fr": "French 🇫🇷",
    "ru": "Russian 🇷🇺",
    "de": "German 🇩🇪",
    "tr": "Turkish 🇹🇷",
    "bn": "Bengali 🇧🇩",
    "th": "Thai 🇹🇭",
    "vi": "Vietnamese 🇻🇳",
    "ja": "Japanese 🇯🇵",
    "zh": "Chinese 🇨🇳",
    "ur": "Urdu 🇵🇰",
    "fa": "Persian 🇮🇷",
    "bho": "Bhojpuri 🇮🇳",
    "ne": "Nepali 🇳🇵",
}


class Language:
    def __init__(self):
        self.lang_codes = lang_codes
        self.lang_dir = Path("MGBMUSIC/locales")
        self.languages = self.load_files()

    def load_files(self):
        languages = {}
        for lang_code in self.lang_codes.keys():
            lang_file = self.lang_dir / f"{lang_code}.json"
            if lang_file.exists():
                with open(lang_file, "r", encoding="utf-8") as file:
                    languages[lang_code] = json.load(file)
        logger.info(f"🌐 Loaded languages: {', '.join(languages.keys())}")
        return languages

    def get_merged_lang(self, lang_code: str) -> dict:
        base = self.languages.get("en", {}).copy()
        if lang_code != "en" and lang_code in self.languages:
            base.update(self.languages[lang_code])
        return base

    async def get_lang(self, chat_id: int) -> dict:
        lang_code = await db.get_lang(chat_id)
        return self.get_merged_lang(lang_code)

    async def get_lang_for(self, user_id: int | None, chat_id: int) -> dict:
        user_code = await db.get_user_lang(user_id) if user_id else None
        lang_code = user_code or await db.get_lang(chat_id)
        return self.get_merged_lang(lang_code)

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                if hasattr(fallen, "chat"):
                    chat = fallen.chat
                elif hasattr(fallen, "message"):
                    chat = fallen.message.chat

                if chat.id in db.blacklisted:
                    try:
                        await chat.leave()
                    except Exception:
                        pass
                    return

                user = getattr(fallen, "from_user", None)
                user_id = user.id if user else None

                lang_dict = await self.get_lang_for(user_id, chat.id)

                setattr(fallen, "lang", lang_dict)
                return await func(*args, **kwargs)

            return wrapper

        return decorator
