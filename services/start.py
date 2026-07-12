"""
Service: Start (video streaming) — SMS code request.

Endpoint: https://api.start.ru/auth/phone/send-code
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "start"
    url = "https://api.start.ru/auth/phone/send-code"
    method = "POST"
    payload_type = "json"
    format_key = "+7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["+7"]}
