"""Service module for Yandex EDA."""

from base_service import BaseService, SendResult


class EdaYandex(BaseService):
    service_name = "eda_yandex"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("+7", phone_formats["7"])
        return {"phone": phone_val}

