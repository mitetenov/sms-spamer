"""Service module for Magnit Apteka."""

from base_service import BaseService, SendResult


class MagnitApteka(BaseService):
    service_name = "magnit_apteka"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"phone": phone_val}

