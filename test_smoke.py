#!/usr/bin/env python3
"""Smoke test — verify all modules import and basic functionality works."""
import sys, os
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

errors = []

# 1. Base module
try:
    from base_service import BaseService, SendResult, SendStatus
    print('OK base_service')
except Exception as e:
    errors.append(f'base_service: {e}')

# 2. Phone utils
try:
    from phone_utils import format_phone_ru, validate_ru_phone
    fmts = format_phone_ru('+79161234567')
    assert validate_ru_phone('+79161234567')
    assert not validate_ru_phone('+12345')
    print('OK phone_utils')
except Exception as e:
    errors.append(f'phone_utils: {e}')

# 3. Stats
try:
    from stats import BombStats, ServiceStats
    stats = BombStats()
    stats.record(SendResult('s1', SendStatus.SUCCESS, 200))
    stats.record(SendResult('s2', SendStatus.FAILED, 400))
    assert stats.total_success == 1
    assert stats.total_failed == 1
    print('OK stats')
except Exception as e:
    errors.append(f'stats: {e}')

# 4. Logger
try:
    from logger import setup_logging
    print('OK logger')
except Exception as e:
    errors.append(f'logger: {e}')

# 5. Service registry
try:
    from services import load_services
    services = load_services()
    assert len(services) > 70
    print(f'OK services: {len(services)} loaded')
except Exception as e:
    errors.append(f'services: {e}')

# 6. Bomber
try:
    from bomber import Bomber
    b = Bomber(concurrency=5)
    print('OK bomber')
except Exception as e:
    errors.append(f'bomber: {e}')

# 7. Validate bot.py syntax
try:
    import py_compile
    py_compile.compile('bot.py', doraise=True)
    print('OK bot.py syntax')
except Exception as e:
    errors.append(f'bot.py: {e}')

if errors:
    print(f'\nERRORS ({len(errors)}):')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)
else:
    print('\nAll tests passed!')
