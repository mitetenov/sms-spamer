"""
Service: Invitro — SMS code request.

Endpoint: https://lk.invitro.ru/lk2/lka/patient/refreshCode
Method: POST
Phone format: 7
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "invitro"
    url = "https://lk.invitro.ru/lk2/lka/patient/refreshCode"
    method = "POST"
    payload_type = "data"
    format_key = "7"
    rate_limit_seconds = 60

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phone": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
