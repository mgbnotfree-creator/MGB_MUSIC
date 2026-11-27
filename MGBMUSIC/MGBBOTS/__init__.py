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
from pathlib import Path


def _list_modules():
    mod_dir = Path(__file__).parent
    modules = []
    for file in mod_dir.rglob("*.py"):
        if file.is_file() and file.name != "__init__.py":
            relative_path = file.relative_to(mod_dir)
            module_path = str(relative_path.with_suffix("")).replace("\\", ".").replace("/", ".")
            modules.append(module_path)
    return modules


all_modules = frozenset(sorted(_list_modules()))
