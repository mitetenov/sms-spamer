"""Generic service implementation loaded from JSON config."""

from base_service import BaseService


class GenericService(BaseService):
    """A service whose behaviour is entirely driven by JSON config."""

    def __init__(self, name: str, config: dict):
        self.service_name = name
        self.url = config["url"]
        self.method = config.get("method", "POST")
        self.payload_type = config.get("payload_type", "data")
        self.success_code = config.get("success_code", 200)
        self.rate_limit_seconds = config.get("rate_limit", 60)
        self.requires_cookies = config.get("requires_cookies", False)
        self.cookies_url = config.get("cookies_url", "")
        self.format_key = config.get("format_key", "+7")
        self._payload_template = config.get("payload_template", "")
        self._custom_headers = config.get("headers", {})

    @classmethod
    def from_config(cls, name: str, config: dict) -> "GenericService":
        return cls(name, config)

    def build_payload(self, phone_formats: dict) -> dict:
        """Build payload by interpolating {phone_FORMAT} or {phone} placeholders."""
        phone_str = phone_formats.get(self.format_key, phone_formats.get("+7", ""))
        template = self._payload_template

        if template:
            # Support {phone} as default placeholder
            raw = template.replace("{phone}", phone_str)
            # Also support explicit format keys like {phone_+7}
            for key, val in phone_formats.items():
                raw = raw.replace(f"{{phone_{key}}}", val)
            # Single key/value: if template is just key=value, convert to dict
            if "=" in raw and not raw.startswith("{"):
                parts = raw.split("&")
                result = {}
                for part in parts:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        result[k] = v
                return result
            # Try to parse as JSON if it looks like JSON
            if raw.strip().startswith("{"):
                import json
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
            # Fallback: return as single key
            return {"phone": phone_str}

        # Default: empty payload (GET requests)
        return {}
