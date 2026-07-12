"""Service module for Tashir Pizza."""

from base_service import BaseService, SendResult


class Tashirpizza(BaseService):
    service_name = "tashirpizza"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone_number": phone_val}

