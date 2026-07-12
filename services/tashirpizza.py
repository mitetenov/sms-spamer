"""Service module for Tashir Pizza."""

from base_service import BaseService, SendResult


class Tashirpizza(BaseService):
    service_name = "tashirpizza"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("parens", phone_formats["7"])
        return {"phone": phone_val}

