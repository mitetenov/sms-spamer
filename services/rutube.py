"""
Service: Rutube — SMS code request.

Endpoint: https://rutube.ru/api/accounts/sendpass/phone
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "rutube"
    url = "https://rutube.ru/api/accounts/sendpass/phone"
    method = "POST"
    payload_type = "data"
    format_key = "+7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
