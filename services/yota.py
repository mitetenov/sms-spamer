"""Service module for Yota TV."""

from base_service import BaseService, SendResult


class Yota(BaseService):
    service_name = "yota"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phoneNumber": phone_val}

