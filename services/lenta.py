"""
Service: Lenta — SMS code request.

Endpoint: https://lenta.com/api/v1/authentication/loginotp
Method: POST
Phone format: 7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "lenta"
    url = "https://lenta.com/api/v1/authentication/loginotp"
    method = "POST"
    payload_type = "json"
    format_key = "7"
    rate_limit_seconds = 120

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["7"]}
