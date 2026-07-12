"""Service module for MTS Free Wi-Fi."""

from base_service import BaseService, SendResult


class MtsFree(BaseService):
    service_name = "mts_free"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

