#!/usr/bin/env python3
"""Validate that all service build_payload methods produce correct payloads.

Tests:
1. Every service's build_payload runs without error
2. Payloads reference self.format_key (no hardcoded keys)
3. Field names are correct per service type
4. URL payload-type services use correct structure
5. Payload types match JSON schema expectations
"""
import sys
sys.path.insert(0, '.')

from phone_utils import format_phone_ru
from services import load_services, get_service


if __name__ == "__main__":
    errors = []
    warnings = []

    # Get test phone formats
    fmts = format_phone_ru('+791****4567')
    print(f"Test phone formats: +791****4567 -> {fmts['+7']}")

    all_services = load_services()
    print(f"\nLoaded {len(all_services)} services\n")

    # Category A: Banks (strictest APIs)
    bank_field_map = {
        'tinkoff': 'phone', 'sberuslugi': 'phone', 'alfa': 'phone',
        'vtb': 'login', 'raif': 'phone', 'akbars': 'phone',
        'sovest': 'phone', 'modulbank': 'phone', 'otkritie': 'phone',
        'gazprom': 'phone', 'rosselhoz': 'phone', 'sovcombank': 'phoneNumber',
        'mkb': 'phone', 'homecredit': 'phone', 'rencredit': 'phone',
        'uralsib': 'phone', 'fastmoney': 'phone', 'qiwi': 'phone',
        'rostel': 'phone', 'sravni': 'phone', 'finuslugi': 'phone',
        'vsk': 'phone', 'pochtabank': 'phoneNumber', 'sber': 'phone',
    }

    # Category D: Telecom
    telecom_field_map = {
        'beeline': 'phoneNumber', 'tele2': 'msisdn', 'megafon_tv': 'phoneNumber',
        'yota': 'phoneNumber', 'mtstv': 'phoneNumber', 'mts_free': 'phoneNumber',
        'wifi_cabinet': 'phone', 'beeline_tv': 'phoneNumber',
    }

    # All known field overrides
    field_map = {**bank_field_map, **telecom_field_map}
    field_map.update({
        'ok': 'st.phone', 'icq': 'phoneNumber', 'telegram': 'phone_number',
        'yandex': 'login', 'magnit': 'PHONE', 'tashirpizza': 'phone_number',
    })

    count_ok = 0
    count_warn = 0
    count_err = 0

    for svc in all_services:
        slug = svc.service_name

        # Test 1: build_payload runs without error
        try:
            payload = svc.build_payload(fmts)
        except Exception as e:
            errors.append(f"  {slug}: build_payload() crashed: {e}")
            count_err += 1
            continue

        # Test 2: payload must be a dict
        if not isinstance(payload, dict):
            errors.append(f"  {slug}: payload is not a dict, got {type(payload).__name__}")
            count_err += 1
            continue

        # Test 3: payload must not be empty
        if len(payload) == 0:
            if svc.method == 'GET':
                pass  # GET can have empty payload
            else:
                warnings.append(f"  {slug}: empty payload for {svc.method} request")
                count_warn += 1
                continue

        # Test 4: payload values must be strings (for data/json)
        for key, val in payload.items():
            if not isinstance(val, str):
                warnings.append(f"  {slug}: value for '{key}' is not a string: {type(val).__name__}")
                count_warn += 1
            if not val:
                errors.append(f"  {slug}: value for '{key}' is empty")
                count_err += 1

        # Test 5: check field name matches expected
        expected_field = field_map.get(slug, 'phone')
        if expected_field != 'phone' and expected_field not in payload:
            warnings.append(f"  {slug}: expected field '{expected_field}' not in payload, got {list(payload.keys())}")
            count_warn += 1

        # Test 6: format key should be used (not hardcoded)
        import inspect
        source = inspect.getsource(svc.build_payload)
        if 'self.format_key' not in source:
            warnings.append(f"  {slug}: does not reference self.format_key")
            count_warn += 1

        count_ok += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Results: {count_ok} OK, {count_warn} warnings, {count_err} errors")
    print(f"{'='*50}")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings[:20]:
            print(w)
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(e)

    # Verify specific known fixes
    print(f"\n{'='*50}")
    print("Verifying known fixes:")
    print(f"{'='*50}")

    # VTB should use "login"
    vtb = get_service('vtb')
    p = vtb.build_payload(fmts)
    assert 'login' in p, f"VTB missing 'login' field: {p}"
    print(f"  VTB: {p}")

    # Tele2 should use "msisdn"
    tele2 = get_service('tele2')
    p = tele2.build_payload(fmts)
    assert 'msisdn' in p, f"Tele2 missing 'msisdn' field: {p}"
    print(f"  Tele2: {p}")

    # OK.ru should use "st.phone"
    ok = get_service('ok')
    p = ok.build_payload(fmts)
    assert 'st.phone' in p, f"OK.ru missing 'st.phone' field: {p}"
    print(f"  OK.ru: {p}")

    # Magnit should use "PHONE"
    magnit = get_service('magnit')
    p = magnit.build_payload(fmts)
    assert 'PHONE' in p, f"Magnit missing 'PHONE' field: {p}"
    print(f"  Magnit: {p}")

    # URL payload services should still work
    for slug in ['sportmaster', 'findclone', 'sipnet', 'tvzavr']:
        svc = get_service(slug)
        p = svc.build_payload(fmts)
        assert isinstance(p, dict), f"{slug} payload not dict"
        print(f"  {slug} (URL): {p}")

    print(f"\n✅ All known fixes verified!" if not errors else f"\n❌ {len(errors)} errors found")
    sys.exit(1 if errors else 0)
