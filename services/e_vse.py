"""Service module for E-vse."""

from base_service import BaseService, SendResult


class EVse(BaseService):
    service_name = "e_vse"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

