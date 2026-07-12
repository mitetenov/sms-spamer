"""Service module for Gorzdrav."""

from base_service import BaseService, SendResult


class Gorzdrav(BaseService):
    service_name = "gorzdrav"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

