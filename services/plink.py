"""Service module for Plink."""

from base_service import BaseService, SendResult


class Plink(BaseService):
    service_name = "plink"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

