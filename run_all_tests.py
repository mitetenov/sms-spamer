#!/usr/bin/env python3
"""Run all test suites sequentially and report results."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

tests = [
    ("test_smoke.py", "Smoke test (imports + service loading)"),
    ("test_integration.py", "Integration test (payloads + stats)"),
    ("test_bot.py", "Bot command unit tests"),
]

passed = 0
failed = 0

for filename, description in tests:
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [sys.executable, filename],
        capture_output=True,
        text=True,
        timeout=60,
    )
    
    # Print stdout (skip long logs)
    lines = result.stdout.strip().split('\n')
    for line in lines[-20:]:  # Show last 20 lines
        print(line)
    
    if result.returncode == 0:
        print(f"\n✅ PASSED: {description}")
        passed += 1
    else:
        print(f"\n❌ FAILED: {description} (exit code {result.returncode})")
        if result.stderr:
            print(f"STDERR: {result.stderr[:500]}")
        failed += 1

print(f"\n{'='*60}")
print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)}")
print(f"{'='*60}")

sys.exit(0 if failed == 0 else 1)
