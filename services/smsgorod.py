"""Service module for SMS Gorod."""

from base_service import BaseService, SendResult


class Smsgorod(BaseService):
    service_name = "smsgorod"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

