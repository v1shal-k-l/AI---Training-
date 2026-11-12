import re

# ----------------------------------
# CONFIG
# ----------------------------------

MAX_INPUT_LENGTH = 500

RESTAURANT_KEYWORDS = [

    "restaurant",
    "restaurants",

    "food",
    "cuisine",
    "dining",

    "cost",
    "price",
    "bill",

    "guest",
    "guests",
    "people",

    "table",
    "seat",
    "seats",

    "indian",
    "italian",
    "chinese",
    "japanese",
    "american"
]

REFUSAL_MESSAGE = (
    "I can only help with restaurant information, "
    "restaurant pricing, cuisines, dining costs, and seating availability."
)

# ----------------------------------
# INPUT VALIDATION
# ----------------------------------


def validate_input(text):

    if not text:
        return False

    if len(text.strip()) == 0:
        return False

    if len(text) > MAX_INPUT_LENGTH:
        return False

    return True


# ----------------------------------
# DOMAIN GUARDRAIL
# ----------------------------------


def is_restaurant_question(text):

    text = text.lower().strip()

    # Allow follow-up responses

    followups = {

        "yes",
        "no",
        "ok",
        "okay",

        "4 people",
        "5 people",
        "6 people",
        "7 people",

        "for 4",
        "for 5",
        "for 6",

        "make that 4 people",
        "make that 5 people",
        "make that 6 people",

        "increase to 4 people",
        "increase to 5 people",
        "increase to 6 people"
    }

    if text in followups:
        return True

    return any(
        keyword in text
        for keyword in RESTAURANT_KEYWORDS
    )


# ----------------------------------
# PII DETECTION
# ----------------------------------


def detect_pii(text):

    email_pattern = (
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    phone_pattern = (
        r"\b[6-9]\d{9}\b"
    )

    if re.search(email_pattern, text):
        return True

    if re.search(phone_pattern, text):
        return True

    return False


# ----------------------------------
# OUTPUT REDACTION
# ----------------------------------


def redact_pii(text):

    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b",
        "[EMAIL REDACTED]",
        text
    )

    text = re.sub(
        r"\b[6-9]\d{9}\b",
        "[PHONE REDACTED]",
        text
    )

    return text


# ----------------------------------
# GUEST VALIDATION
# ----------------------------------


def valid_guest_count(count):

    return (
        isinstance(count, int)
        and
        1 <= count <= 20
    )


# ----------------------------------
# PROMPT INJECTION
# ----------------------------------


def detect_prompt_injection(text):

    attacks = [

        "ignore previous instructions",
        "ignore all instructions",

        "system prompt",
        "developer prompt",

        "show hidden prompt",
        "reveal prompt",

        "forget your instructions",

        "jailbreak",

        "act as another assistant",

        "override policy",

        "bypass guardrails",

        "reveal internal instructions"
    ]

    text = text.lower()

    return any(
        attack in text
        for attack in attacks
    )


# ----------------------------------
# OUTPUT SAFETY
# ----------------------------------


def unsafe_output(text):

    blocked_terms = [

        "password",
        "secret key",
        "api key",
        "access token",
        "credit card"
    ]

    text = text.lower()

    return any(
        item in text
        for item in blocked_terms
    )