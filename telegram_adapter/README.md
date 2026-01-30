# Telegram Adapter for clawd.bot 🔧

This directory contains a minimal Telegram polling adapter written in Python to forward messages between Telegram and `clawd`. It supports three modes:

1. HTTP mode: set `CLAWD_URL` to an HTTP endpoint that accepts POST `{ "text": "..." }` and returns JSON `{ "reply": "..." }`.
2. CLI mode: set `CLAWD_CMD` to a command to run (it will receive the message via stdin and should output the reply to stdout).
3. Fallback: if no `CLAWD_URL`/`CLAWD_CMD` is set, the adapter echoes messages (useful for testing).

## Quick start (local polling)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `TELEGRAM_TOKEN`.

3. Run the bot:

```bash
python bot.py
```

4. (Optional) Use `ngrok http 8080` and configure webhook if you want to switch to webhook mode, but the adapter currently uses polling by default.

## Notes
- Keep your `TELEGRAM_TOKEN` secret. Use environment variables or secrets for deployment.
- When you have a `clawd` HTTP API, set `CLAWD_URL` to integrate directly.
