#!/usr/bin/env python3
"""Test the header and authentication fixes in base_service.py and bomber.py."""
import sys, os
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from base_service import (
    BaseService, SendResult, SendStatus, DEFAULT_HEADERS, _derive_origin_headers
)

errors = []

def check(condition, msg):
    if not condition:
        errors.append(f"FAIL: {msg}")
        print(f"  ❌ {msg}")
    else:
        print(f"  ✅ {msg}")

print("=" * 60)
print("1. DEFAULT_HEADERS fixes")
print("=" * 60)
check("Content-Type" in DEFAULT_HEADERS, "DEFAULT_HEADERS has Content-Type")
check("X-Requested-With" in DEFAULT_HEADERS, "DEFAULT_HEADERS has X-Requested-With")
check(DEFAULT_HEADERS["X-Requested-With"] == "XMLHttpRequest",
      "X-Requested-With is XMLHttpRequest")
check(DEFAULT_HEADERS["Content-Type"] == "application/x-www-form-urlencoded; charset=utf-8",
      "Content-Type default is form-urlencoded")

print("\n" + "=" * 60)
print("2. Origin/Referer derivation")
print("=" * 60)
origin = _derive_origin_headers("https://api.tinkoff.ru/v1/sign_up")
check(origin["Origin"] == "https://api.tinkoff.ru", f"Origin correct: {origin['Origin']}")
check(origin["Referer"] == "https://api.tinkoff.ru/", f"Referer correct: {origin['Referer']}")

origin2 = _derive_origin_headers("http://smsgorod.ru/sendsms.php")
check(origin2["Origin"] == "http://smsgorod.ru", "HTTP origin works")
check(origin2["Referer"] == "http://smsgorod.ru/", "HTTP Referer works")

# Test with nonstandard port
origin3 = _derive_origin_headers("https://mobile.vkusvill.ru:40113/api/user/")
check(origin3["Origin"] == "https://mobile.vkusvill.ru:40113",
      f"Origin with port correct: {origin3['Origin']}")

# Test with bad URL
origin4 = _derive_origin_headers("not a url")
check(origin4 == {}, f"Bad URL returns empty dict: {origin4}")

print("\n" + "=" * 60)
print("3. send_sms() payload routing")
print("=" * 60)

class FakeService(BaseService):
    service_name = "fake"
    def build_payload(self, phone_formats):
        return {"phone": "79001234567"}

async def test_payload_routing():
    svc = FakeService()
    svc.url = "https://example.com/api"
    svc.method = "POST"

    # Test JSON payload routing
    svc.payload_type = "json"
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        call_kwargs = mock_session.request.call_args[1]
        check("json" in call_kwargs, "JSON payload_type uses json=")
        check("data" not in call_kwargs, "JSON payload_type does NOT use data=")
        check("params" not in call_kwargs, "JSON payload_type does NOT use params=")

    # Test data payload routing
    svc.payload_type = "data"
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        call_kwargs = mock_session.request.call_args[1]
        check("data" in call_kwargs, "data payload_type uses data=")
        check("json" not in call_kwargs, "data payload_type does NOT use json=")
        check("params" not in call_kwargs, "data payload_type does NOT use params=")

    # Test URL payload routing (the Bug 1 fix)
    svc.payload_type = "url"
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        call_kwargs = mock_session.request.call_args[1]
        check("params" in call_kwargs, "url payload_type uses params=")
        check("json" not in call_kwargs, "url payload_type does NOT use json=")
        check("data" not in call_kwargs, "url payload_type does NOT use data=")

asyncio.run(test_payload_routing())

print("\n" + "=" * 60)
print("4. Headers built by send_sms()")
print("=" * 60)

async def test_headers():
    svc = FakeService()
    svc.url = "https://api.example.com/v1/send"
    svc.method = "POST"

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        call_kwargs = mock_session.request.call_args[1]
        headers = call_kwargs["headers"]

        check("Content-Type" in headers, "Headers contain Content-Type")
        check("X-Requested-With" in headers, "Headers contain X-Requested-With")
        check("Origin" in headers, "Headers contain Origin")
        check("Referer" in headers, "Headers contain Referer")
        check(headers["Origin"] == "https://api.example.com",
              f"Origin matches service URL domain: {headers['Origin']}")
        check(headers["Referer"] == "https://api.example.com/",
              f"Referer matches service URL: {headers['Referer']}")

    # Test JSON payload_type sets application/json Content-Type
    svc.payload_type = "json"
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        headers = mock_session.request.call_args[1]["headers"]
        check(headers["Content-Type"] == "application/json; charset=utf-8",
              f"JSON payload_type sets Content-Type to application/json: {headers['Content-Type']}")

    # Test data payload_type sets form-urlencoded Content-Type
    svc.payload_type = "data"
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        headers = mock_session.request.call_args[1]["headers"]
        check(headers["Content-Type"] == "application/x-www-form-urlencoded; charset=utf-8",
              f"data payload_type sets Content-Type to form-urlencoded: {headers['Content-Type']}")

asyncio.run(test_headers())

print("\n" + "=" * 60)
print("5. Custom headers merging")
print("=" * 60)

async def test_custom_headers():
    svc = FakeService()
    svc.url = "https://api.totopizza.ru/graphql"
    svc.method = "POST"
    svc.payload_type = "json"
    svc.custom_headers = {
        "Accept": "application/json",
        "X-Custom": "test-value"
    }

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        headers = mock_session.request.call_args[1]["headers"]

        check(headers.get("X-Custom") == "test-value",
              f"Custom header X-Custom preserved: {headers.get('X-Custom')}")
        check(headers.get("Accept") == "application/json",
              f"Custom Accept header set: {headers.get('Accept')}")
        # Origin/Referer should still be derived from URL
        check("Origin" in headers, "Origin still present with custom headers")
        check(headers["Origin"] == "https://api.totopizza.ru",
              f"Origin derived correctly: {headers['Origin']}")

asyncio.run(test_custom_headers())

print("\n" + "=" * 60)
print("6. Cookie passing")
print("=" * 60)

async def test_cookies():
    svc = FakeService()
    svc.url = "https://example.com/api"
    svc.method = "POST"

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        # Pass cookies
        test_cookies = {"session": "abc123", "csrf": "token456"}
        await svc.send_sms({}, mock_session, cookies=test_cookies)
        call_kwargs = mock_session.request.call_args[1]
        check("cookies" in call_kwargs, "cookies kwarg passed to session.request")
        check(call_kwargs["cookies"] == test_cookies,
              f"Cookies match: {call_kwargs['cookies']}")

    # Test without cookies
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session)
        call_kwargs = mock_session.request.call_args[1]
        check("cookies" not in call_kwargs,
              "No cookies kwarg when cookies not provided")

asyncio.run(test_cookies())

print("\n" + "=" * 60)
print("7. Proxy passing preserved")
print("=" * 60)

async def test_proxy():
    svc = FakeService()
    svc.url = "https://example.com/api"
    svc.method = "POST"

    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session, proxy="http://proxy:8080")
        call_kwargs = mock_session.request.call_args[1]
        check(call_kwargs.get("proxy") == "http://proxy:8080",
              f"Proxy passed through: {call_kwargs.get('proxy')}")

    # Test with proxy + cookies together
    with patch("aiohttp.ClientSession") as mock_session_cls:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session = AsyncMock()
        mock_session.request = AsyncMock(return_value=mock_resp)

        await svc.send_sms({}, mock_session, proxy="http://proxy:8080",
                          cookies={"session": "val"})
        call_kwargs = mock_session.request.call_args[1]
        check(call_kwargs.get("proxy") == "http://proxy:8080",
              "Proxy + cookies: proxy passed")
        check(call_kwargs.get("cookies") == {"session": "val"},
              "Proxy + cookies: cookies passed")

asyncio.run(test_proxy())

# Results
print("\n" + "=" * 60)
if errors:
    print(f"❌ {len(errors)} FAILURE(S):")
    for e in errors:
        print(f"   {e}")
    sys.exit(1)
else:
    print("✅ ALL HEADER/AUTHENTICATION FIX TESTS PASSED")
