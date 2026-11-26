<div align="center">

# 🤝 Contributing to MGBMUSIC

Thanks for helping make **MGBMUSIC** better!
Made by **MGB NOT FREE CODER** · [@MGB_NOT_FREE](https://github.com/mgbnotfree-creator/MGBMusic) · [MGBMUSIC](https://t.me/mgb_not_free_coder)

</div>

---

## Ways to help

- 🐛 **Report bugs** — open an [issue](https://github.com/mgbnotfree-creator/MGBMusic/issues) with logs and steps to reproduce
- 💡 **Suggest features** — explain the problem first, then your idea
- 🌐 **Translate** — add or improve a language in `MGBMUSIC/locales/`
- 🧩 **Send code** — fix a bug, add a plugin, improve docs
- 🔐 **Found a security problem?** Do **not** open an issue — read [SECURITY.md](SECURITY.md)

For quick questions, ask in the support group: [MGBMUSIC](https://t.me/mgb_not_free_coder) or channel: [MGB_SUPPROT_GROUP](https://t.me/MGB_SUPPROT_GROUP).

---

## Before you start

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) (how the bot works) and [Structure.md](Structure.md) (where files live).
2. Check open issues / PRs so you don't duplicate work.
3. For big changes, open an issue first and describe your plan.

---

## Local setup

**Requirements:** Python 3.10+, FFmpeg, a MongoDB database (local or Atlas), a bot token, and a separate Telegram account for the assistant. See the [README](README.md#-requirements).

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone [https://github.com/](https://github.com/)<your-username>/MGBMusic
cd MGBMusic

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -U -r requirements.txt

# 4. Configure (use a TEST bot, a TEST group and a TEST database)
cp MGBMUSIC.env .env
nano .env                         # fill in the values

# 5. Run
bash start                        # or: python -m MGBMUSIC
