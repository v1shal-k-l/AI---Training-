import re

REFUSAL_MESSAGE = (
    "Request cannot be processed because it "
    "violates security or data protection policies."
)

MAX_TEXT_LENGTH = 2000

PII_PATTERNS = [
    r"\b\d{12}\b",  # Aadhaar
    r"\b\d{16}\b",  # Credit Card
    r"\b\d{10}\b",  # Phone Number
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
]

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "reveal prompt",
    "developer instructions",
    "bypass policy",
    "jailbreak",
    "act as administrator",
    "override instructions"
]

SQL_INJECTION_PATTERNS = [
    "drop table",
    "truncate table",
    "delete from",
    "union select",
    "' or 1=1",
    "\" or 1=1",
    "--",
    ";--",
    "xp_cmdshell"
]

XSS_PATTERNS = [
    "<script>",
    "</script>",
    "javascript:",
    "onerror=",
    "onload=",
    "<iframe",
    "</iframe>"
]

SENSITIVE_OUTPUT_PATTERNS = [
    "credit card",
    "cvv",
    "password",
    "api_key",
    "access_token",
    "secret_key",
    "aadhaar"
]


def validate_length(text: str):
    """
    Prevent excessively large inputs.
    """

    if not text:
        return True

    return len(str(text)) <= MAX_TEXT_LENGTH


def contains_pii(text: str):
    """
    Detect common PII.
    """

    if not text:
        return False

    text = str(text)

    for pattern in PII_PATTERNS:

        if re.search(pattern, text):
            return True

    return False


def detect_prompt_injection(text: str):
    """
    Detect prompt injection attempts.
    """

    if not text:
        return False

    text = str(text).lower()

    for pattern in PROMPT_INJECTION_PATTERNS:

        if pattern in text:
            return True

    return False


def detect_sql_injection(text: str):
    """
    Detect SQL injection fingerprints.
    """

    if not text:
        return False

    text = str(text).lower()

    for pattern in SQL_INJECTION_PATTERNS:

        if pattern in text:
            return True

    return False


def detect_xss(text: str):
    """
    Detect XSS attempts.
    """

    if not text:
        return False

    text = str(text).lower()

    for pattern in XSS_PATTERNS:

        if pattern in text:
            return True

    return False


def output_contains_sensitive_data(text: str):
    """
    Prevent sensitive data leakage.
    """

    if not text:
        return False

    text = str(text).lower()

    for pattern in SENSITIVE_OUTPUT_PATTERNS:

        if pattern in text:
            return True

    return False


def run_input_guardrails(text: str):

    if not validate_length(text):
        return False, "Input exceeds allowed length."

    if contains_pii(text):
        return False, "PII detected."

    if detect_prompt_injection(text):
        return False, "Prompt injection attempt detected."

    if detect_sql_injection(text):
        return False, "SQL injection attempt detected."

    if detect_xss(text):
        return False, "XSS attempt detected."

    return True, "VALID"


def run_output_guardrails(text: str):

    if output_contains_sensitive_data(text):
        return False

    return True
