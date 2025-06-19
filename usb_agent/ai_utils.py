SENSITIVE_KEYWORDS = [
    "turkish armed forces",
    "secret",
    "confidential",
]


def is_sensitive(text: str) -> bool:
    text_lower = text.lower()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            return True
    return False
