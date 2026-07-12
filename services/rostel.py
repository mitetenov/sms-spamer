"""
Service: Rostelecom — SMS code request.

Endpoint: https://rt.ru/api/auth/send-code
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "rostel"
    url = "https://rt.ru/api/auth/send-code"
    method = "POST"
    payload_type = "json"
    format_key = "+7"
    rate_limit_seconds = 120

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
