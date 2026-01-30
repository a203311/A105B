"""Webhook server for Telegram to forward updates to clawd and respond.

Run with: uvicorn webhook:app --host 0.0.0.0 --port ${PORT:-8000}
"""
import os
import logging
import requests
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from clawd import get_clawd_reply

logger = logging.getLogger("telegram_webhook")
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN 未设置，webhook 无法发送回复")

WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = FastAPI()

class Message(BaseModel):
    message: Optional[dict]


@app.post("/telegram/webhook")
async def telegram_webhook(req: Request, update: Message, x_telegram_bot_api_secret_token: Optional[str] = Header(None)):
    # Verify secret token if configured
    if WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
            logger.warning("Webhook secret mismatch: %s", x_telegram_bot_api_secret_token)
            raise HTTPException(status_code=403, detail="forbidden")

    if not update.message:
        return {"ok": True}

    msg = update.message
    chat_id = None
    text = None

    # message can be nested; handle simple text messages
    chat = msg.get("chat")
    if chat:
        chat_id = chat.get("id")

    text = msg.get("text")
    if not chat_id or not text:
        # not a text message we handle
        return {"ok": True}

    logger.info("Received webhook message from %s: %s", chat_id, text)

    # get reply from CLAWD
    reply = await get_clawd_reply(text)

    # call Telegram sendMessage
    send_url = f"{TELEGRAM_API}/sendMessage"
    try:
        r = requests.post(send_url, json={"chat_id": chat_id, "text": reply}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logger.exception("Failed to send message to Telegram: %s", e)
        raise HTTPException(status_code=500, detail="failed to send message")

    return {"ok": True}
