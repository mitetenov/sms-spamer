"""Service module for Stockmann."""

from base_service import BaseService, SendResult


class Stockmann(BaseService):
    service_name = "stockmann"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("parens", phone_formats["7"])
        return {"phone": phone_val}

