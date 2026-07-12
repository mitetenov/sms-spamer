"""Service module for Wi-Fi.ru."""

from base_service import BaseService, SendResult


class WifiCabinet(BaseService):
    service_name = "wifi_cabinet"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

