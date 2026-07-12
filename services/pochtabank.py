"""
Service: PochtaBank — SMS code request.

Endpoint: https://my.pochtabank.ru/dbo/registrationService/ib/phoneNumber
Method: PUT
Phone format: +7

NOTE: Requires cookies — a GET to cookies_url first for PHPSESSID/CSRF.
"""
from base_service import BaseService

class Service(BaseService):
    service_name = "pochtabank"
    url = "https://my.pochtabank.ru/dbo/registrationService/ib/phoneNumber"
    method = "PUT"
    payload_type = "json"
    format_key = "+7"
    rate_limit_seconds = 120
    requires_cookies = True
    cookies_url = "https://my.pochtabank.ru/"

    def build_payload(self, phone_formats: dict) -> dict:
        """Build the request payload with the correct phone format."""
        return {"phoneNumber": phone_formats.get(self.format_key) or phone_formats.get("+7", "")}
