"""Service module for Sovcombank."""

from base_service import BaseService, SendResult


class Sovcombank(BaseService):
    service_name = "sovcombank"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phoneNumber": phone_val}

