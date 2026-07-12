"""
Service: Globus (delivery/grocery) — SMS code request.

Endpoint: https://globus.ru/api/auth/sms/send
Method: POST
Phone format: 7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "globus"
    url = "https://globus.ru/api/auth/sms/send"
    method = "POST"
    payload_type = "json"
    format_key = "7"
    rate_limit_seconds = 120

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
