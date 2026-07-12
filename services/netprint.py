"""Service module for NetPrint."""

from base_service import BaseService, SendResult


class Netprint(BaseService):
    service_name = "netprint"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone": phone_val}

