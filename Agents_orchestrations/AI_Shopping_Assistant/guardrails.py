import re

MAX_INPUT_LENGTH = 500
def contains_pii(text):

    patterns = [

        # Email
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        # Phone
        r"\b[6-9]\d{9}\b",

        # Aadhaar
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",

        # PAN
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",

        # Credit Card
        r"\b(?:\d{4}[- ]?){3}\d{4}\b",

        # Secret Keys
        r"sk-[A-Za-z0-9]+",

    ]

    for pattern in patterns:

        if re.search(pattern, text):
            return True

    return False


def validate_input(text):

    return (
        text
        and
        len(text.strip()) > 0
        and
        len(text) <= MAX_INPUT_LENGTH
    )


def detect_pii(text):

    email = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    phone = (
        r"\b[6-9]\d{10}\b"
    )

    return (
        re.search(email, text)
        or
        re.search(phone, text)
    )


def redact_pii(text):

    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b",
        "[EMAIL REDACTED]",
        text
    )

    text = re.sub(
        r"\b[6-9]\d{9,10}\b",
        "[PHONE REDACTED]",
        text
    )

    return text


def detect_prompt_injection(text):

    attacks = [

        "ignore previous instructions",
        "reveal system prompt",
        "developer prompt",
        "jailbreak",
        "override policy"
    ]

    text = text.lower()

    return any(
        attack in text
        for attack in attacks
    )
