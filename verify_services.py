"""Verify all 20 service modules are importable and functional."""
import sys
sys.path.insert(0, '.')

from base_service import BaseService, SendResult, SendStatus
from phone_utils import format_phone_ru
from services.registry import load_services, get_service_names

# Test phone formatting
variants = format_phone_ru('+79161234567')
assert variants['+7'] == '+79161234567'
assert variants['7'] == '79161234567'
assert variants['8'] == '89161234567'
assert variants['short'] == '9161234567'
print('[PASS] phone_utils.format_phone_ru')

# Test registry
services = load_services()
names = get_service_names()
assert len(services) == 20, f'Expected 20, got {len(services)}'
assert len(names) == 20
print(f'[PASS] registry: {len(services)} services loaded')

# Test each service
for svc in services:
    name = svc.service_name
    assert svc.url.startswith('http'), f'{name}: bad URL'
    assert svc.method in ('GET', 'POST', 'PUT'), f'{name}: bad method'
    assert svc.payload_type in ('json', 'data', 'url'), f'{name}: bad payload_type'
    assert svc.format_key in variants, f'{name}: bad format_key'
    assert svc.rate_limit_seconds > 0, f'{name}: bad rate_limit'

    payload = svc.build_payload('+79161234567')
    assert isinstance(payload, dict), f'{name}: payload not dict'
    assert len(payload) > 0, f'{name}: empty payload'

    # Verify phone made it into the payload
    payload_str = str(payload)
    assert '916' in payload_str or '7916' in payload_str, f'{name}: no phone in payload'

print(f'[PASS] All 20 services validated individually')

# List all
print(f'\nService registry ({len(names)}):')
for n in sorted(names):
    print(f'  - {n}')

print('\n=== ALL CHECKS PASSED ===')
