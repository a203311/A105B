"""Telegram adapter for clawd.bot (polling mode).

Usage:
  - Set environment variable TELEGRAM_TOKEN
  - Optionally set CLAWD_URL (HTTP endpoint) or CLAWD_CMD (CLI command).
    If neither is set, the adapter echoes messages as a placeholder.

Run:
  python telegram_adapter/bot.py
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from telegram_adapter.clawd import get_clawd_reply

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ clawd.bot Adapter 已连接。发送消息以获取回复。")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("发送任意文本，适配器会把文本转交给 clawd（本地或远端），并把回复返回给你。")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info("收到消息: %s", user_text)
    reply = await get_clawd_reply(user_text)
    await update.message.reply_text(reply)


def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("请设置环境变量 TELEGRAM_TOKEN")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
