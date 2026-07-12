"""Service module for Yandex."""

from base_service import BaseService, SendResult


class Yandex(BaseService):
    service_name = "yandex"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"login": phone_val}

