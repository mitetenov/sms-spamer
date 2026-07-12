"""Service module for Apteka.ru."""

from base_service import BaseService, SendResult

class AptekaRu(BaseService):
    service_name = "apteka_ru"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("parens", phone_formats["7"])
        return {"phone": phone_val}

