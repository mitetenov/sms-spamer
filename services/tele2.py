"""Service module for Tele2."""

from base_service import BaseService, SendResult


class Tele2(BaseService):
    service_name = "tele2"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

