"""Base service interface for SMS bomber modules."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from urllib.parse import urlparse

import aiohttp

log = logging.getLogger("smsbot.service")


class SendStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


@dataclass
class SendResult:
    service_name: str
    status: SendStatus
    http_status: Optional[int] = None
    error: Optional[str] = None
    response_preview: Optional[str] = None
    elapsed: float = 0.0

    @property
    def is_success(self) -> bool:
        return self.status == SendStatus.SUCCESS

    @property
    def is_error(self) -> bool:
        return self.status in (
            SendStatus.FAILED,
            SendStatus.TIMEOUT,
            SendStatus.BLOCKED,
        )


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

SUCCESS_CODES = {200, 201, 202, 204}
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRIES = 2
RETRY_DELAY = 1.0  # seconds between retries


class BaseService(ABC):
    """Abstract base for all SMS bomber services.

    Each service module in services/ subclasses this and implements:
      - service_name (class attr): short slug e.g. 'tinkoff'
      - build_payload(phone: str) -> dict
    """

    service_name: str = ""
    url: str = ""
    method: str = "POST"
    payload_type: str = "json"  # "json", "data", "url"
    success_code: int = 200
    rate_limit_seconds: int = 60
    requires_cookies: bool = False
    cookies_url: str = ""
    format_key: str = "+7"  # phone format variant to use
    verify_ssl: bool = True  # set False for services with bad certs

    @abstractmethod
    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload using formatted phone variants."""
        ...

    def _add_referer(self, headers: dict) -> None:
        """Add a Referer header derived from the service URL."""
        try:
            parsed = urlparse(self.url)
            origin = f"{parsed.scheme}://{parsed.netloc}"
            headers["Referer"] = f"{origin}/"
        except Exception:
            pass

    def _interpolate_url(self, phone_formats: dict) -> str:
        """Replace {phone} and {phone_FORMAT} placeholders in the URL."""
        result = self.url
        for key, val in phone_formats.items():
            result = result.replace(f"{{phone_{key}}}", val)
        phone = phone_formats.get(self.format_key, phone_formats.get("+7", ""))
        result = result.replace("{phone}", phone)
        return result

    async def send_sms(
        self,
        phone_formats: dict,
        session: aiohttp.ClientSession,
        proxy: Optional[str] = None,
    ) -> SendResult:
        """Send an SMS code request to this service.

        Args:
            phone_formats: Dict of phone format variants from format_phone_ru()
            session: Shared aiohttp session
            proxy: Optional proxy URL

        Returns:
            SendResult with status and metadata
        """
        import asyncio
        import time

        start = time.monotonic()
        last_error = None
        last_http_status = None

        url = self._interpolate_url(phone_formats)

        for attempt in range(MAX_RETRIES + 1):
            try:
                payload = self.build_payload(phone_formats)
                headers = dict(DEFAULT_HEADERS)
                self._add_referer(headers)

                kwargs = {
                    "headers": headers,
                    "timeout": aiohttp.ClientTimeout(total=15),
                    "ssl": self.verify_ssl,
                }
                if proxy:
                    kwargs["proxy"] = proxy

                if self.payload_type == "json":
                    kwargs["json"] = payload
                else:
                    kwargs["data"] = payload

                async with session.request(
                    self.method, url, **kwargs
                ) as resp:
                    elapsed = time.monotonic() - start
                    if resp.status in SUCCESS_CODES:
                        return SendResult(
                            self.service_name,
                            SendStatus.SUCCESS,
                            resp.status,
                            elapsed=elapsed,
                        )
                    elif resp.status in (429, 503):
                        return SendResult(
                            self.service_name,
                            SendStatus.RATE_LIMITED,
                            resp.status,
                            elapsed=elapsed,
                        )
                    elif resp.status in RETRYABLE_STATUSES and attempt < MAX_RETRIES:
                        body = await resp.text()
                        last_error = body[:200]
                        last_http_status = resp.status
                        log.warning(
                            f"🔄 {self.service_name}: HTTP {resp.status}, "
                            f"retry {attempt + 1}/{MAX_RETRIES}"
                        )
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    else:
                        body = await resp.text()
                        return SendResult(
                            self.service_name,
                            SendStatus.FAILED,
                            resp.status,
                            error=body[:200],
                            elapsed=elapsed,
                        )
            except asyncio.TimeoutError:
                elapsed = time.monotonic() - start
                last_error = "timeout"
                if attempt < MAX_RETRIES:
                    log.warning(
                        f"🔄 {self.service_name}: TIMEOUT, "
                        f"retry {attempt + 1}/{MAX_RETRIES}"
                    )
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                return SendResult(
                    self.service_name, SendStatus.TIMEOUT, elapsed=elapsed
                )
            except Exception as e:
                elapsed = time.monotonic() - start
                last_error = str(e)
                error_lower = str(e).lower()
                if any(kw in error_lower for kw in (
                    "name or service not known", "dns", "no address",
                    "nodename nor servname", "getaddrinfo",
                )):
                    return SendResult(
                        self.service_name,
                        SendStatus.FAILED,
                        error=str(e),
                        elapsed=elapsed,
                    )
                if any(kw in error_lower for kw in (
                    "certificate verify failed", "ssl", "tlsv1",
                )):
                    log.warning(
                        f"🔓 {self.service_name}: SSL error, "
                        f"retrying without verification"
                    )
                    self.verify_ssl = False
                    continue
                if attempt < MAX_RETRIES:
                    log.warning(
                        f"🔄 {self.service_name}: {e}, "
                        f"retry {attempt + 1}/{MAX_RETRIES}"
                    )
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                return SendResult(
                    self.service_name,
                    SendStatus.FAILED,
                    error=str(e),
                    elapsed=elapsed,
                )

        return SendResult(
            self.service_name,
            SendStatus.FAILED,
            http_status=last_http_status,
            error=last_error or "max retries exceeded",
            elapsed=time.monotonic() - start,
        )
