import sys
import os
import asyncio

# NOTE: we insert the repo root into PYTHONPATH inside the test function
# to avoid module-level imports after executable statements (E402).


def test_clawd_echo():
    # Ensure repository root is on PYTHONPATH for CI
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    from telegram_adapter.clawd import get_clawd_reply

    reply = asyncio.run(get_clawd_reply("hello world"))
    assert "回显" in reply or "echo" in reply
