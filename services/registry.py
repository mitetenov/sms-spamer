"""Service registry — loads services from services.json and instantiates them.

The registry reads the centralized services.json file and dynamically
imports each service module, configuring the BaseService subclass with
the endpoint details.
"""

import json
import importlib
import os
from typing import Optional

from base_service import BaseService


_SERVICES_JSON = os.path.join(os.path.dirname(__file__), "services.json")


def load_service_configs() -> dict:
    """Load raw service configurations from services.json."""
    with open(_SERVICES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def get_service(slug: str) -> Optional[BaseService]:
    """Instantiate a single service by its slug name."""
    configs = load_service_configs()
    if slug not in configs:
        return None

    cfg = configs[slug]
    try:
        module = importlib.import_module(f"services.{slug}")
        # Find the BaseService subclass in the module
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if (isinstance(obj, type) and issubclass(obj, BaseService)
                    and obj is not BaseService):
                svc = obj()
                # Override class attrs from JSON config
                svc.url = cfg.get("url", svc.url)
                svc.method = cfg.get("method", svc.method)
                svc.payload_type = cfg.get("payload_type", svc.payload_type)
                svc.format_key = cfg.get("format_key", svc.format_key)
                svc.success_code = cfg.get("success_code", svc.success_code)
                svc.rate_limit_seconds = cfg.get("rate_limit_seconds", svc.rate_limit_seconds)
                svc.requires_cookies = cfg.get("requires_cookies", svc.requires_cookies)
                svc.cookies_url = cfg.get("cookies_url", svc.cookies_url)
                return svc
    except (ImportError, ModuleNotFoundError) as e:
        print(f"[WARN] Could not load service '{slug}': {e}")
        return None

    return None


def load_services(
    categories: Optional[list[str]] = None,
    exclude: Optional[set[str]] = None,
) -> list[BaseService]:
    """Load and instantiate all service modules.

    Args:
        categories: Optional list of category letters to include (e.g. ['A', 'B'])
        exclude: Optional set of service slugs to exclude

    Returns:
        List of instantiated BaseService subclasses ready to use
    """
    configs = load_service_configs()
    services = []

    for slug in sorted(configs):
        if exclude and slug in exclude:
            continue
        cfg = configs[slug]
        if categories and cfg.get("category", "") not in categories:
            continue

        svc = get_service(slug)
        if svc is not None:
            services.append(svc)

    return services


def get_category_stats() -> dict[str, int]:
    """Return counts of services per category."""
    configs = load_service_configs()
    stats = {}
    for slug, cfg in configs.items():
        cat = cfg.get("category", "?")
        stats[cat] = stats.get(cat, 0) + 1
    return dict(sorted(stats.items()))


if __name__ == "__main__":
    # Quick self-test
    svcs = load_services()
    print(f"Loaded {len(svcs)} services")
    for svc in svcs[:5]:
        print(f"  {svc.service_name}: {svc.method} {svc.url[:60]}...")
    if len(svcs) > 5:
        print(f"  ... and {len(svcs) - 5} more")
    print(f"\nCategory breakdown: {get_category_stats()}")
