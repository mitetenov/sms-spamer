#!/usr/bin/env python3
"""Comprehensive integration test — payload validation, stats, concurrent execution."""

import sys, os
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

from base_service import BaseService, SendResult, SendStatus
from phone_utils import format_phone_ru, validate_ru_phone
from stats import BombStats, ServiceStats
from services import load_services

errors = []
test_phone = '+79001234567'
phone_formats = format_phone_ru(test_phone)

print("="*60)
print("1. Phone formatting")
print("="*60)
assert phone_formats['+7'].startswith('+79') and len(phone_formats['+7']) == 12
assert phone_formats['7'].isdigit() and len(phone_formats['7']) == 11
assert phone_formats['8'].startswith('89') and len(phone_formats['8']) == 11
assert phone_formats['short'].isdigit() and len(phone_formats['short']) == 10
assert validate_ru_phone('+79001234567')
assert validate_ru_phone('89001234567')
assert validate_ru_phone('9001234567')
assert not validate_ru_phone('+12345')
print("PASS phone_utils")

print("\n" + "="*60)
print("2. Stats accuracy")
print("="*60)
stats = BombStats()
stats.record(SendResult('s1', SendStatus.SUCCESS, 200))
stats.record(SendResult('s2', SendStatus.FAILED, 400))
stats.record(SendResult('s3', SendStatus.TIMEOUT))
stats.record(SendResult('s4', SendStatus.RATE_LIMITED, 429))
stats.record(SendResult('s5', SendStatus.BLOCKED, 403))

assert stats.total_success == 1, f"total_success: {stats.total_success}"
assert stats.total_failed == 1, f"total_failed: {stats.total_failed}"
assert stats.total_errors == 3, f"total_errors (FAILED+TIMEOUT+BLOCKED): {stats.total_errors}"
assert stats.total_rate_limited == 1, f"total_rate_limited: {stats.total_rate_limited}"
assert stats.total == 4, f"total (success + errors): {stats.total}"
print("PASS stats counters")

# Test save/load round-trip
stats.mark_finished()
stats.save('/tmp/test_bomber_stats.json')
loaded = BombStats.load('/tmp/test_bomber_stats.json')
assert loaded.total_success == 1
assert loaded.total_failed == 1
assert loaded.total_errors == 3
assert loaded.total_rate_limited == 1
print("PASS stats save/load")

# Test summary string
summary = stats.summary()
assert 'Success' in summary
assert 'Failed' in summary
assert 'Rate Limited' in summary
print("PASS stats summary")

print("\n" + "="*60)
print("3. Service payload validation")
print("="*60)
services = load_services()
assert len(services) == 111, f"Expected 111 services, got {len(services)}"
print(f"Loaded {len(services)} services")

failures = []
for svc in services:
    name = svc.service_name
    try:
        payload = svc.build_payload(phone_formats)
        assert isinstance(payload, dict), f"{name}: payload not dict"
        assert len(payload) > 0, f"{name}: empty payload"
        # Check phone is somewhere in the payload
        payload_str = str(payload)
        if '900' not in payload_str and '7900' not in payload_str and '+7900' not in payload_str \
           and '9001' not in payload_str:
            failures.append(f"{name}: no phone in payload: {payload_str}")
    except Exception as e:
        failures.append(f"{name}: {e}")

if failures:
    print(f"\nFAILURES ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
else:
    print(f"All {len(services)} services build valid payloads!")

print("\n" + "="*60)
print("4. Bomber smoke test")
print("="*60)
from bomber import Bomber

# Test bomber instantiation and basic lifecycle
b = Bomber(concurrency=5, round_delay=0.1)
assert b.is_running == False
assert b.stats.total == 0
b.stop()
print("PASS bomber lifecycle")

# Test stats tracking simulates concurrent send outcomes
b2 = Bomber(concurrency=3, round_delay=0.01)
fmts = format_phone_ru(test_phone)

# Simulate what _send_one does: record result
services = load_services()[:10]
for i, svc in enumerate(services):
    if i < 6:
        result = SendResult(svc.service_name, SendStatus.SUCCESS, 200, elapsed=0.5)
    elif i < 8:
        result = SendResult(svc.service_name, SendStatus.TIMEOUT, elapsed=15.0)
    elif i < 9:
        result = SendResult(svc.service_name, SendStatus.FAILED, 400, error="bad request", elapsed=0.3)
    else:
        result = SendResult(svc.service_name, SendStatus.RATE_LIMITED, 429, elapsed=0.2)
    b2.stats.record(result)

assert b2.stats.total_success == 6
assert b2.stats.total_errors == 3  # 2 timeout + 1 failed
assert b2.stats.total_failed == 1
assert b2.stats.total_rate_limited == 1
assert b2.stats.total == 9  # 6 success + 3 errors
print(f"PASS concurrent send simulation ({b2.stats.total} total, {b2.stats.total_success} success, {b2.stats.total_errors} errors)")
print(b2.stats.summary())

print("\n" + "="*60)
print("5. Category breakdown")
print("="*60)
from services.registry import get_category_stats
cats = get_category_stats()
print(f"Categories: {cats}")
print(f"Total: {sum(cats.values())}")

print("\n" + "="*60)
print("6. Config & env defaults")
print("="*60)
import bot as bot_module
assert bot_module.STATS_FILE == "bomber_stats.json"
assert bot_module.LOG_FILE == "bomber.log"
assert bot_module.CONCURRENCY == 15
print("PASS config defaults")

if failures:
    print(f"\n❌ {len(failures)} FAILURE(S) in payload validation!")
    sys.exit(1)
else:
    print("\n✅ ALL INTEGRATION TESTS PASSED")
