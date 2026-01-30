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

---

## Webhook mode (production)

1. Set environment variables:

```bash
export TELEGRAM_TOKEN="your-telegram-token"
export TELEGRAM_WEBHOOK_SECRET="some-long-secret"
export WEBHOOK_URL="https://yourdomain.com/telegram/webhook"
```

2. Deploy the service (example using Docker):

```bash
docker build -t clawd-telegram:latest -f telegram_adapter/Dockerfile .
docker run -e TELEGRAM_TOKEN=$TELEGRAM_TOKEN -e TELEGRAM_WEBHOOK_SECRET=$TELEGRAM_WEBHOOK_SECRET -e CLAWD_URL=$CLAWD_URL -p 8000:8000 clawd-telegram:latest
```

3. Set Telegram webhook (use same secret token):

```bash
curl -F "url=$WEBHOOK_URL" -F "secret_token=$TELEGRAM_WEBHOOK_SECRET" https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook
```

The webhook endpoint is `POST /telegram/webhook` and will verify the `X-Telegram-Bot-Api-Secret-Token` header.

## Notes
- Keep your `TELEGRAM_TOKEN` secret. Use environment variables or secrets for deployment.
- When you have a `clawd` HTTP API, set `CLAWD_URL` to integrate directly.
