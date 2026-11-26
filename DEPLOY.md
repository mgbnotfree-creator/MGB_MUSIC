# 🚀 Deploy Guide

Sab platforms Docker use karte hain (ffmpeg install ho jata hai → music + animated welcome card dono chalte hain).

## Environment variables
| Variable | Zaroori | Kya hai |
|---|---|---|
| `BOT_TOKEN` | ✅ | @BotFather se bot token |
| `STRING_SESSION` | ✅ | Assistant account ka Pyrogram v2 session |
| `MONGO_DB_URI` | ✅ | MongoDB connection string |
| `OWNER_ID` | ✅ | Aapki Telegram ID |
| `LOGGER_ID` | ✅ | Logger group ID (`-100…`). **Song cache bhi isi se chalta hai** |
| `MGBMUSIC_KEY` | ✅ | MGBMUSIC API key. Log in at https://artistbotsapi.bond to get it |
| `API_ID`, `API_HASH` | ✅ | my.telegram.org se |
| `MGBMUSIC_API_URL` | ❌ | Default `https://api.artistbotsapi.bond` |

Bot ko Logger group me add karke admin banao (cache ke liye file bhejne ki permission chahiye).

## Render
1. Repo GitHub par push karo (`https://github.com/mgbnotfree-creator/MGBMusic`).
2. Render → **New → Blueprint** → repo select karo (`render.yaml` apne aap padh leta hai).
3. Env variables bharo → Deploy.
   *Free web service 15 min idle par sleep ho jati hai; 24x7 ke liye `plan: starter` karo ya uptime monitor se `/` ping karo.*

## Heroku
```bash
heroku create your-app-name
heroku stack:set container
heroku config:set BOT_TOKEN=... STRING_SESSION=... MONGO_DB_URI=... OWNER_ID=... LOGGER_ID=... MGBMUSIC_KEY=... API_ID=... API_HASH=...
git push heroku main
heroku ps:scale worker=1

## VPS / local (Docker)
```bash
cp Artist.env .env      # fill karo
docker compose up -d --build
docker compose logs -f
```

## VPS bina Docker
```bash
sudo bash setup         # ffmpeg, node etc. install
pip install -r requirements.txt
bash start
```
