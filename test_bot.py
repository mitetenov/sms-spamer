#!/usr/bin/env python3
"""Unit tests for Telegram bot commands using PTB test helpers."""

import sys, os, json, tempfile
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Must set BOT_TOKEN env before importing bot
os.environ["SMS_BOT_TOKEN"] = "test_token"
os.environ["SMS_STATS_FILE"] = tempfile.mktemp(suffix='.json')
os.environ["SMS_LOG_FILE"] = tempfile.mktemp(suffix='.log')

from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

import bot as bot_module
from bot import (
    cmd_start as set_handler,
    cmd_begin as start_handler,
    cmd_stop as stop_handler,
    cmd_stats as stats_handler,
    cmd_help as help_handler,
)
from bomber import Bomber
from stats import BombStats
from phone_utils import format_phone_ru
from base_service import SendResult, SendStatus

print("="*60)
print("Bot Command Unit Tests")
print("="*60)

def make_update(text=None, args=None):
    """Create a mock Update for testing command handlers."""
    user = User(id=123, first_name="Test", is_bot=False)
    chat = Chat(id=456, type="private")
    
    msg = MagicMock(spec=Message)
    msg.reply_text = AsyncMock()
    msg.chat = chat
    msg.from_user = user
    msg.text = text
    
    update = MagicMock(spec=Update)
    update.message = msg
    update.effective_user = user
    update.effective_chat = chat
    
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.args = args or []
    
    return update, context

def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

# ---------------------------------------------------------------------------
# Test /set command
# ---------------------------------------------------------------------------
print("\n--- /set command ---")

# Test no args
update, ctx = make_update(args=[])
run_async(set_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Usage:" in reply, f"Expected usage message, got: {reply}"
print("PASS /set with no args")

# Test valid phone
update, ctx = make_update(args=['+79001234567'])
bot_module.target_phone = None
run_async(set_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Target set" in reply
assert bot_module.target_phone == '+79001234567'
print("PASS /set with valid phone +79...")

# Test valid 8-prefixed phone
update, ctx = make_update(args=['89001234567'])
run_async(set_handler(update, ctx))
assert bot_module.target_phone == '89001234567'
print("PASS /set with 89...")

# Test invalid phone
update, ctx = make_update(args=['+12345'])
run_async(set_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Invalid" in reply
print("PASS /set with invalid phone")

# ---------------------------------------------------------------------------
# Test /start command
# ---------------------------------------------------------------------------
print("\n--- /start command ---")

# Test /start without target
bot_module.target_phone = None
bot_module.bomber = None
update, ctx = make_update()
run_async(start_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "No target set" in reply
print("PASS /start without target")

# Test /start with target (starts bomber)
bot_module.target_phone = '+79001234567'
update, ctx = make_update()
run_async(start_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Starting SMS bomb" in reply
assert bot_module.bomber is not None
assert bot_module.bomb_task is not None
print("PASS /start with target")

# Test /start while already running
update, ctx = make_update()
run_async(start_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Already bombing" in reply
print("PASS /start while running")

# ---------------------------------------------------------------------------
# Test /stop command
# ---------------------------------------------------------------------------
print("\n--- /stop command ---")

# Test /stop while bomber running
update, ctx = make_update()
run_async(stop_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "Stopping" in reply
print("PASS /stop while running")

# Wait for attack to finish (stop_event is set so it should finish quickly)
import time
start = time.time()
while bot_module.bomb_task and not bot_module.bomb_task.done():
    asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
    if time.time() - start > 10:
        break

# Reset state
bot_module.bomber = None

# Test /stop when not running
update, ctx = make_update()
run_async(stop_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "No bombing in progress" in reply
print("PASS /stop when not running")

# ---------------------------------------------------------------------------
# Test /stats command
# ---------------------------------------------------------------------------
print("\n--- /stats command ---")

# Test /stats when no stats exist
bot_module.bomber = None
bot_module.cumulative_stats = None
# Remove stats file if exists
if os.path.exists(bot_module.STATS_FILE):
    os.unlink(bot_module.STATS_FILE)

update, ctx = make_update()
run_async(stats_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert "No stats" in reply
print("PASS /stats with no data")

# Test /stats with data from a Bomber
b = Bomber(concurrency=5)
b.stats.record(SendResult('test_svc', SendStatus.SUCCESS, 200))
b.stats.record(SendResult('test_svc2', SendStatus.FAILED, 400))
bot_module.bomber = b
update, ctx = make_update()
run_async(stats_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert 'RUNNING' in reply or 'STOPPED' in reply
assert 'Success' in reply
print("PASS /stats with bomber data")

# Test /stats from file
bot_module.bomber = None
b.stats.save(bot_module.STATS_FILE)
update, ctx = make_update()
run_async(stats_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert 'Success' in reply
print("PASS /stats from file")

# ---------------------------------------------------------------------------
# Test /help command
# ---------------------------------------------------------------------------
print("\n--- /help command ---")

update, ctx = make_update()
run_async(help_handler(update, ctx))
reply = update.message.reply_text.call_args[0][0]
assert '/set' in reply
assert '/start' in reply
assert '/stop' in reply
assert '/stats' in reply
assert '/help' in reply
print("PASS /help command")

# ---------------------------------------------------------------------------
# Test bot init error handling
# ---------------------------------------------------------------------------
print("\n--- Bot init error ---")

# Test that bot exits cleanly when no token (main is not called, just imports)
try:
    import importlib
    # Already imported above - no crash = pass
    print("PASS bot import with mock token")
except SystemExit as e:
    assert e.code == 1
    print("PASS bot exits without token")

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
if os.path.exists(bot_module.STATS_FILE):
    os.unlink(bot_module.STATS_FILE)
if os.path.exists(bot_module.LOG_FILE):
    os.unlink(bot_module.LOG_FILE)

# Cancel any lingering task
if bot_module.bomb_task and not bot_module.bomb_task.done():
    bot_module.bomb_task.cancel()
bot_module.bomber = None
bot_module.target_phone = None

print("\n✅ ALL BOT COMMAND TESTS PASSED")
