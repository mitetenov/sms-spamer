"""Service module for Telegram."""

from base_service import BaseService, SendResult


class Telegram(BaseService):
    service_name = "telegram"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone_number": phone_val}

