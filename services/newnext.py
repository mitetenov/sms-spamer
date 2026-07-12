"""Service module for NewNext."""

from base_service import BaseService, SendResult


class Newnext(BaseService):
    service_name = "newnext"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

