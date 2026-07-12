"""Service module for VTB."""

from base_service import BaseService, SendResult


class Vtb(BaseService):
    service_name = "vtb"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"login": phone_val}

