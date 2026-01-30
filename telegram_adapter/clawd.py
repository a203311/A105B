"""CLAWD integration helpers for Telegram adapter.

Provides async-compatible helper to obtain replies from CLAWD via HTTP or CLI.
"""
import os
import shlex
import subprocess
import logging
import asyncio
import requests

logger = logging.getLogger(__name__)


async def get_clawd_reply(text: str) -> str:
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
