"""Service module for Yaponchik."""

from base_service import BaseService, SendResult


class Yaponchik(BaseService):
    service_name = "yaponchik"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("parens", phone_formats["7"])
        return {"phone": phone_val}

