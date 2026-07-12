"""Service module for UTair."""

from base_service import BaseService, SendResult


class Utair(BaseService):
    service_name = "utair"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("8", phone_formats["7"])
        return {"phone": phone_val}

