import sys, os
sys.path.insert(0, '/root/sms-spamer')

# Try importing everything bot.py uses
try:
    import telethon
    from bomber import Bomber
    from logger import setup_logging
    from phone_utils import format_phone_ru, validate_ru_phone
    from stats import BombStats
    print('OK: All imports successful (bot would start if token were set)')
except ModuleNotFoundError as e:
    print(f'FAIL: ModuleNotFoundError: {e}')
    sys.exit(1)
