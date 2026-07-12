"""Service module for ICQ."""

from base_service import BaseService, SendResult


class Icq(BaseService):
    service_name = "icq"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phoneNumber": phone_val}

