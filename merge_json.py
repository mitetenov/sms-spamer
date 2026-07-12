#!/usr/bin/env python3
"""Merge the 20 services from t_df5e23ce into the main services.json."""
import json

# Load current services.json
with open('services/services.json') as f:
    main = json.load(f)

# Load the 20 services from t_df5e23ce parent
with open('/root/.hermes/kanban/boards/sms-spamer/workspaces/t_df5e23ce/services/services.json') as f:
    extra = json.load(f)

# Define categories for the 20 services
categories = {
    'rostel': 'A', 'sber': 'A', 'yoomoney': 'B', 'rutube': 'C',
    'vsk': 'A', 'invitro': 'D', 'lenta': 'E', 'cian': 'F',
    'dns': 'F', 'start': 'G', 'finuslugi': 'A', 'pochtabank': 'A',
    'globus': 'E', 'delimobil': 'H', 'ekapusta': 'B', 'joymoney': 'B',
    'zaimer': 'B', 'sravni': 'A', 'platiza': 'B', 'beeline_tv': 'G',
}

# Convert to standard format
for slug, cfg in extra.items():
    if slug in main:
        continue
    main[slug] = {
        "slug": slug,
        "label": cfg.get("label", slug.replace('_', ' ').title()),
        "url": cfg["url"],
        "method": cfg["method"],
        "payload_type": cfg.get("payload_type", "json"),
        "format_key": cfg.get("format_key", "+7"),
        "success_code": cfg.get("success_code", 200),
        "rate_limit_seconds": cfg.get("rate_limit_seconds", 60),
        "requires_cookies": cfg.get("requires_cookies", False),
        "cookies_url": cfg.get("cookies_url", ""),
        "category": categories.get(slug, "X"),
    }
    print(f"Added: {slug}")

print(f"\nTotal services in JSON: {len(main)}")

with open('services/services.json', 'w') as f:
    json.dump(main, f, indent=2, ensure_ascii=False)
print("Done!")
