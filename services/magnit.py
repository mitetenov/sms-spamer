"""Service module for Magnit."""

from base_service import BaseService, SendResult


class Magnit(BaseService):
    service_name = "magnit"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"PHONE": phone_val}

