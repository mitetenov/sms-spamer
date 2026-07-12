"""Service module for B-Apteka."""

from base_service import BaseService, SendResult

class BApteka(BaseService):
    service_name = "b_apteka"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

