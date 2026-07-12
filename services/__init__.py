"""SMS bomber service modules package.

Each module implements a BaseService subclass for a specific
Russian service that sends SMS verification codes.

All services are loaded via registry.py from services.json.
"""

from services.registry import load_services, get_service

__all__ = ["load_services", "get_service"]
