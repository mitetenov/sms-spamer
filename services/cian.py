"""
Service: Cian (real estate) — SMS code request.

Endpoint: https://api.cian.ru/auth/send-code/
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "cian"
    url = "https://api.cian.ru/auth/send-code/"
    method = "POST"
    payload_type = "json"
    format_key = "+7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["+7"]}
