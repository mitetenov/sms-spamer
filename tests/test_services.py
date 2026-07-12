#!/usr/bin/env python3
"""Verify all service modules load correctly."""
import sys
sys.path.insert(0, '.')

from base_service import BaseService, SendResult, SendStatus
from phone_utils import format_phone_ru

# Test phone formatting
formats = format_phone_ru('+79161234567')
print('Phone formats:', {k: v for k, v in sorted(formats.items())})

# Test a few service imports
from services import load_services, get_service

svc = get_service('tinkoff')
print(f'Tinkoff: {svc.service_name} -> {svc.method} {svc.url[:50]}...')

# Load all services
all_svcs = load_services()
print(f'\nTotal services loaded: {len(all_svcs)}')

# Show first few
for s in all_svcs[:5]:
    print(f'  {s.service_name}: {s.method} {s.url[:60]}')

# Show categories from services.json
from services.registry import get_category_stats
print(f'\nCategory breakdown: {get_category_stats()}')

# Verify all explicitly named services from task
required = ['tinkoff', 'raif', 'sunlight', 'yandex', 'avito', 'megafon_tv',
            'mtstv', 'beeline', 'tele2', 'vtb', 'alfa', 'ozon', 'wildberries',
            'vkusvill']
print(f'\nVerifying required services:')
for slug in required:
    svc = get_service(slug)
    status = 'OK' if svc else 'MISSING'
    print(f'  {slug}: {status}')

# Verify payload building
from phone_utils import format_phone_ru
fmts = format_phone_ru('+79161234567')
for slug in ['tinkoff', 'yandex', 'avito']:
    svc = get_service(slug)
    payload = svc.build_payload(fmts)
    print(f'\n  {slug} payload: {payload}')
