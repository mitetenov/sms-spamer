"""Service module for Yaponchik."""

from base_service import BaseService, SendResult


class Yaponchik(BaseService):
    service_name = "yaponchik"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone": phone_val}

