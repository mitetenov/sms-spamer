"""
Service: Ekapusta (microloans) — SMS code request.

Endpoint: https://ekapusta.com/api/v1/auth/request-sms
Method: POST
Phone format: 7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "ekapusta"
    url = "https://ekapusta.com/api/v1/auth/request-sms"
    method = "POST"
    payload_type = "json"
    format_key = "7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["7"]}
