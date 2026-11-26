<div align="center">

# 🗂️ Project Structure

Where everything lives in **MGBMUSIC**.
Made by **MGB NOT FREE CODER** · [@MGB_NOT_FREE](https://github.com/mgbnotfree-creator/MGBMusic) · [MGBMUSIC](https://t.me/mgb_not_free_coder)

</div>

> New here? Read [ARCHITECTURE.md](ARCHITECTURE.md) for *how* the pieces work together. This file only tells you *where* things are.

---

## Top level

```text
MGBMUSIC/
├── MGBMUSIC/                 # The bot's Python package (all source code)
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI (syntax + locale check) and Docker/Render/Fly deploy
├── .dockerignore             # Files excluded from the Docker build context
├── .gitignore                # Files Git must never track (.env, sessions, cache, …)
├── MGBMUSIC.env              # Environment variable TEMPLATE → copy to .env and fill in
├── config.py                 # Reads env vars into the Config object
├── requirements.txt          # Python dependencies
├── start                     # Start command:  python3 -m MGBMUSIC
├── setup                     # VPS helper script (ffmpeg, deno, pip install, creates .env)
├── Dockerfile                # Image: python 3.10 + ffmpeg + node
├── docker-compose.yml        # Run on a VPS with Docker
├── Procfile                  # Heroku/Procfile-style worker command
├── heroku.yml                # Heroku container deploy
├── railway.json              # Railway deploy settings
├── render.yaml               # Render Blueprint
├── fly.toml                  # Fly.io settings
├── app.json                  # Heroku "Deploy" button manifest
├── README.md                 # Project overview, features, commands
├── DEPLOY.md                 # Step-by-step deploy guide
├── ARCHITECTURE.md           # How the bot works internally
├── Structure.md              # This file
├── CONTRIBUTING.md           # How to contribute
├── SECURITY.md               # Security policy & hardening checklist
└── LICENSE                   # MIT License + project details & credits
