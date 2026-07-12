"""Phone number formatting utilities for Russian numbers."""

import re
from typing import Dict


def format_phone_ru(raw: str) -> Dict[str, str]:
    """Parse a raw phone input and return all common Russian format variants.

    Accepts: '+7XXXYYYZZZZ', '8XXXYYYZZZZ', '7XXXYYYZZZZ', 'XXXYYYZZZZ' (10 digits)

    Returns a dict with keys: '+7', '7', '8', 'parens', 'parens2',
    'spaces', 'short', 'dash'
    """
    digits = re.sub(r"\D", "", raw)

    if len(digits) == 10:
        digits = "7" + digits
    elif len(digits) == 11:
        if digits[0] == "8":
            digits = "7" + digits[1:]
        elif digits[0] != "7":
            digits = "7" + digits
    else:
        # fallback: keep as-is
        pass

    # Now digits should be '7XXXXXXXXXX' (11 digits)
    code = digits[1:4]   # 3-digit area code
    part1 = digits[4:7]  # 3 digits
    part2 = digits[7:9]  # 2 digits
    part3 = digits[9:11] # 2 digits

    return {
        "+7": "+" + digits,                             # +71234567890
        "7": digits,                                    # 71234567890
        "8": "8" + digits[1:],                          # 81234567890
        "parens": f"+7 ({code}) {part1}-{part2}-{part3}",     # +7 (123) 456-78-90
        "parens2": f"7 ({code}) {part1}-{part2}-{part3}",     # 7 (123) 456-78-90
        "spaces": f"+7 {code} {part1} {part2} {part3}",       # +7 123 456 78 90
        "short": digits[1:],                            # 1234567890 (10 digits)
        "dash": f"+7-{code}-{part1}-{part2}-{part3}",         # +7-123-456-78-90
    }


def validate_ru_phone(raw: str) -> bool:
    """Check if the input is a valid Russian mobile number."""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return digits[0] == "9"
    elif len(digits) == 11:
        return digits[0] in ("7", "8") and digits[1] == "9"
    return False
