"""Service module for Avito."""

from base_service import BaseService, SendResult

class Avito(BaseService):
    service_name = "avito"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone": phone_val}

