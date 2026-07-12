"""Service module for OK.ru."""

from base_service import BaseService, SendResult


class Ok(BaseService):
    service_name = "ok"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get(self.format_key) or phone_formats.get("+7", "")
        return {"st.phone": phone_val}

