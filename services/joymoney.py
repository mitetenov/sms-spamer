"""
Service: Joymoney (microloans) — SMS code request.

Endpoint: https://joy.money/api/v1/auth/login/phone
Method: POST
Phone format: 7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "joymoney"
    url = "https://joy.money/api/v1/auth/login/phone"
    method = "POST"
    payload_type = "json"
    format_key = "7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["7"]}
