"""Service module for Alpari."""

from base_service import BaseService, SendResult

class Alparip(BaseService):
    service_name = "alparip"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

