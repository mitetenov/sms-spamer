#!/usr/bin/env python3
"""Fix build_payload signatures across all service modules to match BaseService.send_sms."""

import os
import re
import sys

SERVICES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services')

fixed_a = 0
fixed_b = 0
skipped = 0

for fname in sorted(os.listdir(SERVICES_DIR)):
    if not fname.endswith('.py') or fname in ('__init__.py', 'registry.py', 'generic_service.py'):
        continue
    
    fpath = os.path.join(SERVICES_DIR, fname)
    with open(fpath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    changed = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # --- Fix Group A: two-arg signature ---
        if 'def build_payload(self, phone: str, phone_formats: dict)' in line:
            line = line.replace(
                'def build_payload(self, phone: str, phone_formats: dict)',
                'def build_payload(self, phone_formats: dict)'
            )
            changed = True
            fixed_a += 1
        
        # --- Fix Group B: one-arg (phone: str) signature ---
        elif 'def build_payload(self, phone: str) -> dict' in line:
            line = line.replace(
                'def build_payload(self, phone: str) -> dict',
                'def build_payload(self, phone_formats: dict) -> dict'
            )
            changed = True
            fixed_b += 1
        
        # Remove format_phone_ru import (if present and service was fixed)
        elif line.strip() == 'from phone_utils import format_phone_ru':
            # Check if this file is a Group B (we already changed signature above)
            # Only remove if we actually changed the signature in this file
            if changed:
                new_lines.append(line)  # keep for now; will handle after
            else:
                new_lines.append(line)
            continue
        
        # Replace phone_variants = format_phone_ru(phone) with nothing
        if changed and re.search(r'phone_variants\s*=\s*format_phone_ru\(phone\)', line):
            # Skip this line
            i += 1
            continue
        
        # Replace phone_variants references with phone_formats
        if changed and 'phone_variants' in line:
            line = line.replace('phone_variants', 'phone_formats')
        
        new_lines.append(line)
        i += 1
    
    if changed:
        # Remove empty lines (consecutive blank lines -> single blank line)
        text = ''.join(new_lines)
        # Clean up: remove import if no longer used
        text = re.sub(r'from phone_utils import format_phone_ru\n', '', text)
        # Clean up double blank lines
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        with open(fpath, 'w') as f:
            f.write(text)
        print(f'Fixed: {fname}')

print(f'\nGroup A fixed: {fixed_a}')
print(f'Group B fixed: {fixed_b}')
