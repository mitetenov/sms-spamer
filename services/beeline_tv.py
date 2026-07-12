"""
Service: Beeline TV — SMS code request.

Endpoint: https://api.beeline.ru/auth/send-code
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "beeline_tv"
    url = "https://api.beeline.ru/auth/send-code"
    method = "POST"
    payload_type = "json"
    format_key = "+7"
    rate_limit_seconds = 120

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phoneNumber": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
