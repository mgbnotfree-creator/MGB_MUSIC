<div align="center">

# 🔐 Security Policy

**MGBMUSIC** — MGBMUSIC API Telegram Music Bot
Made by **MGB NOT FREE CODER** · [@MGB_NOT_FREE](https://github.com/mgbnotfree-creator/MGBMusic) · [MGBMUSIC](https://t.me/mgb_not_free_coder)

</div>

---

## Supported Versions

Security fixes go to the latest release line only.

| Version | Supported |
|:---:|:---:|
| 3.0.x | ✅ |
| < 3.0 | ❌ |

---

## Reporting a Vulnerability

**Please do not open a public issue or post details in the support group.**

1. **Preferred:** use GitHub's private reporting —
   [Report a vulnerability](https://github.com/mgbnotfree-creator/MGBMusic/security/advisories/new)
   (Repository → *Security* → *Report a vulnerability*).
2. **Alternative:** message the admins of the support group
   [MGBMUSIC](https://t.me/mgb_not_free_coder) or channel [MGB_SUPPROT_GROUP](https://t.me/MGB_SUPPROT_GROUP) and ask for a private contact.
   Share **only** that you have a security report — send the details privately.

Please include:

- What the problem is and which file / command / variable is affected
- Steps to reproduce (a minimal example is best)
- The impact you think it has (data leak, takeover, crash, …)
- Your bot version (`MGBMUSIC/__init__.py` → `__version__`) and how you deploy

**What to expect (best effort, this is a solo-maintained project):**

| Step | Target |
|---|---|
| Acknowledgement | within a few days |
| Fix or mitigation plan | as soon as it is confirmed |
| Credit in the release notes | yes, unless you prefer to stay anonymous |

---

## Scope

**In scope**

- Bypassing owner / sudo / admin / auth checks (e.g. a normal user running `/eval`, `/broadcast`, `/gban`, `/restart`)
- Leaking `BOT_TOKEN`, `STRING_SESSION`, `MONGO_DB_URI`, `API_HASH`, `MGBMUSIC_KEY` or cookies through logs, messages or errors
- Code / command injection (shell, ffmpeg, yt-dlp arguments, Mongo queries)
- Path traversal or unsafe file handling in downloads, cache or sticker tools
- Denial-of-service that one user can trigger against the whole bot

**Out of scope**

- Problems in Telegram itself, Pyrogram / kurigram, py-tgcalls, MongoDB, yt-dlp or FFmpeg (report those upstream)
- External API services themselves
- A deployer leaving their own secrets public, or running with a weak setup (see the checklist below)
- Spam, FloodWait or rate limits caused by normal use
- Social engineering

---

## 🛡️ Hardening checklist for people who deploy the bot

**Secrets**

- [ ] Keep every secret in environment variables or a local `.env`. **Never** commit `.env`, `*.session`, cookies or a filled-in `MGBMUSIC.env`.
- [ ] Never hardcode tokens, hashes or database URLs as defaults in `config.py` or anywhere else in the code.
- [ ] Use **your own** `API_ID` / `API_HASH` from [my.telegram.org](https://my.telegram.org).
- [ ] If a secret was ever pushed to GitHub, treat it as **leaked**: rotate it (BotFather `/revoke`, new MongoDB password, terminate the Telegram session, new API key). Deleting the commit is not enough — Git history and forks keep it.
- [ ] Turn on GitHub **Secret scanning** and **Push protection** for your repo.

**Telegram accounts**

- [ ] Use a **separate Telegram account** for the assistant (`STRING_SESSION`). Never use your main account.
- [ ] Enable two-step verification on the owner account and on the assistant account.
- [ ] Keep the **logger group private** — it receives logs and the song cache.
- [ ] Give the bot only the admin rights it needs.

**Owner power**

- [ ] `OWNER_ID` can run `/eval` and `/exec`, which execute code on your server. Protect that Telegram account like a root login.
- [ ] Add sudo users (`/addsudo`) only if you fully trust them; sudo users can broadcast, gban, blacklist and restart.

**Database**

- [ ] Create a MongoDB user with access to the bot's database only (not an admin user).
- [ ] Use a strong, unique password and restrict network access (IP allow-list) where your host supports it.
- [ ] Keep regular backups.

**Server & container**

- [ ] Keep dependencies updated (`pip install -U -r requirements.txt`, rebuild the image regularly).
- [ ] Do not run the bot as root on a VPS; use the provided Docker setup or a normal user.
- [ ] YouTube cookies (`COOKIE_URL`) are account credentials. Use a throw-away account and a private paste link.

---

## Responsible Disclosure

Give a reasonable amount of time to fix the issue before sharing it publicly.
Good-faith research that follows this policy will not be treated as hostile.

---

<div align="center">

Made with ❤️ by **MGB NOT FREE CODER** · Powered by **MGBMUSIC**
[GitHub](https://github.com/mgbnotfree-creator/MGBMusic) · [Group](https://t.me/mgb_not_free_coder) · [Channel](https://t.me/MGB_SUPPROT_GROUP)

</div>
