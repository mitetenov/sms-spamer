"""Service module for Zdes Apteka."""

from base_service import BaseService, SendResult


class Zdesapteka(BaseService):
    service_name = "zdesapteka"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("parens", phone_formats["7"])
        return {"phone": phone_val}

