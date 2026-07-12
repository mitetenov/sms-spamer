"""
Service: Sberbank — SMS code request.

Endpoint: https://www.sberbank.ru/auth/register/confirm
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "sber"
    url = "https://www.sberbank.ru/auth/register/confirm"
    method = "POST"
    payload_type = "data"
    format_key = "+7"
    rate_limit_seconds = 120

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
