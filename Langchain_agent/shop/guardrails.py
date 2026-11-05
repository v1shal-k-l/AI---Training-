import re

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

MAX_INPUT_LENGTH = 500

MAX_PARTICIPANTS = 100

REFUSAL_MESSAGE = (
    "I can only assist with workshop-related information, "
    "fees, discounts, and coupon calculations."
)

ALLOWED_TOOLS = {
    "list_all_workshops",
    "find_cheapest_workshop",
    "search_workshops",
    "calculate_workshop_fee",
    "apply_coupon",
}

ALLOWED_COUPONS = {
    "WELCOME10",
    "PYTHON10",
    "AI10"
}


# ---------------------------------------------------
# INPUT LENGTH
# ---------------------------------------------------

def validate_length(text):

    return len(text) <= MAX_INPUT_LENGTH


# ---------------------------------------------------
# DOMAIN GUARDRAIL
# ---------------------------------------------------

def is_workshop_question(text):

    keywords = [

        "workshop",
        "training",
        "course",
        "python",
        "azure",
        "ai",
        "machine learning",
        "data science",
        "price",
        "cost",
        "fee",
        "discount",
        "coupon",

    ]

    text = text.lower()

    return any(
        keyword in text
        for keyword in keywords
    )


# ---------------------------------------------------
# PII INPUT DETECTION
# ---------------------------------------------------

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


# ---------------------------------------------------
# PROMPT INJECTION
# ---------------------------------------------------

def detect_prompt_injection(text):

    attacks = [

        "ignore previous instructions",

        "ignore all instructions",

        "act as",

        "system prompt",

        "developer prompt",

        "jailbreak",

        "override safety",

        "reveal hidden",

        "show internal prompt",

        "bypass restrictions",

        "forget your instructions",

        "execute code",

        "list all secrets",

        "show coupon database",

    ]

    text = text.lower()

    return any(
        attack in text
        for attack in attacks
    )


# ---------------------------------------------------
# SQL INJECTION
# ---------------------------------------------------

def detect_sql_injection(text):

    patterns = [

        r"drop\s+table",

        r"delete\s+from",

        r"union\s+select",

        r"insert\s+into",

        r"update\s+\w+",

        r"--",

        r";"

    ]

    text = text.lower()

    for pattern in patterns:

        if re.search(pattern, text):
            return True

    return False


# ---------------------------------------------------
# XSS DETECTION
# ---------------------------------------------------

def detect_xss(text):

    patterns = [

        "<script",

        "</script>",

        "javascript:",

        "<iframe",

        "onerror=",

        "onclick=",

    ]

    text = text.lower()

    return any(
        pattern in text
        for pattern in patterns
    )


# ---------------------------------------------------
# TOOL WHITELIST
# ---------------------------------------------------

def validate_tool(tool):

    return tool in ALLOWED_TOOLS


# ---------------------------------------------------
# PARTICIPANT VALIDATION
# ---------------------------------------------------

def validate_participants(count):

    return (
        isinstance(count, int)
        and 1 <= count <= MAX_PARTICIPANTS
    )


# ---------------------------------------------------
# COUPON VALIDATION
# ---------------------------------------------------

def validate_coupon(code):

    return (
        code.upper()
        in ALLOWED_COUPONS
    )


# ---------------------------------------------------
# OUTPUT CHECK
# ---------------------------------------------------

def output_contains_sensitive_data(text):

    blocked = [

        "password",

        "secret",

        "api key",

        "credit card",

        "aadhaar",

        "pan number",

    ]

    text = text.lower()

    return any(
        word in text
        for word in blocked
    )


# ---------------------------------------------------
# RATE LIMIT
# ---------------------------------------------------

class RateLimiter:

    def __init__(
        self,
        limit=25
    ):
        self.limit = limit
        self.count = 0

    def allow(self):

        self.count += 1

        return (
            self.count <= self.limit
        )