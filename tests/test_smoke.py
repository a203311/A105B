import asyncio

from telegram_adapter.clawd import get_clawd_reply


def test_clawd_echo():
    reply = asyncio.run(get_clawd_reply("hello world"))
    assert "回显" in reply or "echo" in reply
