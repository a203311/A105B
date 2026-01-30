"""Telegram adapter for clawd.bot (polling mode).

Usage:
  - Set environment variable TELEGRAM_TOKEN
  - Optionally set CLAWD_URL (HTTP endpoint) or CLAWD_CMD (CLI command). If neither is set, the adapter echoes messages as a placeholder.

Run:
  python telegram_adapter/bot.py
"""

import os
import logging
import asyncio
import shlex
import subprocess

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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

async def get_clawd_reply(text: str) -> str:
    """Obtain a reply from clawd.

    Priority:
      1. HTTP endpoint via CLAWD_URL -> POST {"text": text}, expect JSON with key 'reply'
      2. CLI via CLAWD_CMD (command receives input on stdin; output on stdout)
      3. Fallback: local echo placeholder
    """
    cla_w_url = os.getenv("CLAWD_URL")
    cla_w_cmd = os.getenv("CLAWD_CMD")

    if cla_w_url:
        try:
            return await asyncio.to_thread(call_clawd_http, cla_w_url, text)
        except Exception as e:
            logger.exception("CLAWD HTTP 调用失败")
            return f"⚠️ 调用 CLAWD HTTP 失败: {e}"

    if cla_w_cmd:
        try:
            return await asyncio.to_thread(call_clawd_cmd, cla_w_cmd, text)
        except Exception as e:
            logger.exception("CLAWD CMD 调用失败")
            return f"⚠️ 运行 CLAWD 命令失败: {e}"

    # fallback placeholder
    return f"（CLAWD 未配置）回显: {text}"


def call_clawd_http(url: str, text: str) -> str:
    r = requests.post(url, json={"text": text}, timeout=10)
    r.raise_for_status()
    try:
        j = r.json()
        return j.get("reply") or j.get("response") or j.get("text") or str(j)
    except ValueError:
        return r.text or "(empty response)"


def call_clawd_cmd(cmd: str, text: str) -> str:
    parts = shlex.split(cmd)
    p = subprocess.run(parts, input=text, text=True, capture_output=True, timeout=30)
    out = p.stdout.strip() or p.stderr.strip()
    return out or "(no output)"


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
