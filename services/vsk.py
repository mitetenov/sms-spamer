"""
Service: VSK Insurance — SMS code request.

Endpoint: https://shop.vsk.ru/ajax/auth/postSms/
Method: POST
Phone format: +7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "vsk"
    url = "https://shop.vsk.ru/ajax/auth/postSms/"
    method = "POST"
    payload_type = "data"
    format_key = "+7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats["+7"]}
