"""Service module for Delivery Club."""

from base_service import BaseService, SendResult


class DeliveryClub(BaseService):
    service_name = "delivery_club"

    def build_payload(self, phone_formats: dict) -> dict:
        phone_val = phone_formats.get("7", phone_formats["7"])
        return {"phone": phone_val}

