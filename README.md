# SMS Bomber Telegram Bot

Async Telegram bot that sends SMS verification code requests to 111 Russian services concurrently.

## Quick Start

```bash
# 1. Install dependencies
pip install --break-system-packages python-telegram-bot aiohttp

# 2. Set your Telegram bot token
export SMS_BOT_TOKEN='your_bot_token_from_BotFather'

# 3. (Optional) Configure
export SMS_CONCURRENCY=15        # services per round (default: 15)
export SMS_STATS_FILE='bomber_stats.json'
export SMS_LOG_FILE='bomber.log'
export SMS_LOG_LEVEL='INFO'      # DEBUG, INFO, WARNING, ERROR

# 4. Run
python3 bot.py
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/set <phone>` | Store target Russian phone number |
| `/start` | Begin bombing (concurrent requests to all services) |
| `/stop` | Gracefully halt the current run |
| `/stats` | Show success/failure/rate-limit counts per service |
| `/help` | Show usage and examples |

Phone formats accepted: `+79XXXXXXXXX`, `89XXXXXXXXX`, `9XXXXXXXXX` (10 digits).

## Architecture

```
bot.py              — Telegram bot entry point (python-telegram-bot)
bomber.py            — Async orchestrator (round-based concurrent execution)
base_service.py       — Abstract BaseService with aiohttp send_sms()
phone_utils.py        — Russian phone formatting (8 variants)
stats.py              — Aggregate + per-service stats (JSON persistence)
logger.py             — Colored console logging + file output
services/
  __init__.py          — Package init
  registry.py          — JSON-driven service loader (reads services.json)
  services.json        — 111 service endpoint definitions (categories A-J)
  generic_service.py   — GenericService for JSON-only services
  <name>.py            — 111 thin BaseService subclasses (~12 lines each)
```

## Service Categories

| Category | Count | Examples |
|----------|-------|----------|
| A (Banks) | 24 | Tinkoff, Alfa, VTB, Sber, Raiffeisen |
| B (Finance) | 17 | Qiwi, YooMoney, Zaimer, Ekapusta |
| C (Telecom) | 10 | Beeline, Tele2, Yota, MTS Free |
| D (Insurance) | 8 | Alfa Insurance, Ingosstrah, VSK |
| E (Retail) | 11 | Ozon, Wildberries, Lenta, Magnit |
| F (Classifieds) | 8 | Avito, Cian, Youla, DNS |
| G (Entertainment) | 8 | Rutube, IVI, OK, Twitch |
| H (Delivery/Taxi) | 10 | Yandex Taxi, Delivery Club, KFC |
| I (Misc) | 5 | Telegram, Tinder, ICQ |
| J (Services) | 10 | Gorzdrav, Apteka.ru, Invitro |

## Testing

```bash
# Smoke test (imports + service loading)
python3 test_smoke.py

# Integration test (payload validation + stats accuracy)
python3 test_integration.py

# Bot command unit tests (all 5 commands + error paths)
python3 test_bot.py
```

## Adding a New Service

1. Create `services/<slug>.py`:

```python
from base_service import BaseService

class ServiceName(BaseService):
    service_name = "slug"
    url = "https://api.example.com/auth/send-code"
    method = "POST"
    payload_type = "json"   # "json", "data", or "url"
    format_key = "+7"       # phone format variant

    def build_payload(self, phone_formats: dict) -> dict:
        return {"phone": phone_formats[self.format_key]}
```

2. Add entry to `services/services.json`:

```json
"slug": {
  "slug": "slug",
  "label": "Service Name",
  "url": "https://api.example.com/auth/send-code",
  "method": "POST",
  "payload_type": "json",
  "format_key": "+7",
  "success_code": 200,
  "rate_limit_seconds": 60,
  "requires_cookies": false,
  "cookies_url": "",
  "category": "X"
}
```

## Configuration Reference

All settings via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SMS_BOT_TOKEN` | *(required)* | Telegram bot token from @BotFather |
| `SMS_CONCURRENCY` | `15` | Services per round |
| `SMS_STATS_FILE` | `bomber_stats.json` | Stats persistence path |
| `SMS_LOG_FILE` | `bomber.log` | Log file path |
| `SMS_LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
