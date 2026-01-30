import sys
import os
import asyncio

# Ensure repository root is on PYTHONPATH for CI
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram_adapter.clawd import get_clawd_reply


def test_clawd_echo():
    reply = asyncio.run(get_clawd_reply("hello world"))
    assert "回显" in reply or "echo" in reply
