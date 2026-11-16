from datetime import datetime

MAX_QUESTION_LENGTH = 500
MAX_DESTINATION_LENGTH = 100
MAX_PURPOSE_LENGTH = 300

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "reveal prompt",
    "show .env",
    "api key",
    "database password",
    "jailbreak",
    "disable guardrails"
]


def validate_dates(start_date, end_date):
    try:

        start = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        ).date()

        today = datetime.today().date()

        if start < today:
            return (
                False,
                "Travel date cannot be in the past."
            )

        if end < start:
            return (
                False,
                "End date cannot be before start date."
            )

        return True, ""

    except Exception:

        return (
            False,
            "Invalid date format. Use YYYY-MM-DD."
        )


def validate_destination(destination):

    if not destination:
        return (
            False,
            "Destination is required."
        )

    if len(destination) > MAX_DESTINATION_LENGTH:
        return (
            False,
            "Destination name too long."
        )

    return True, ""


def validate_purpose(purpose):

    if len(purpose) > MAX_PURPOSE_LENGTH:
        return (
            False,
            "Purpose exceeds maximum length."
        )

    return True, ""


def validate_question(question):

    if len(question) > MAX_QUESTION_LENGTH:

        return (
            False,
            "Question exceeds maximum length."
        )

    return True, ""


def detect_prompt_injection(text):

    text = text.lower()

    for pattern in INJECTION_PATTERNS:

        if pattern in text:
            return True

    return False


def run_trip_guardrails(
    destination,
    purpose,
    start_date,
    end_date
):

    valid, message = validate_destination(
        destination
    )

    if not valid:
        return False, message

    valid, message = validate_purpose(
        purpose
    )

    if not valid:
        return False, message

    valid, message = validate_dates(
        start_date,
        end_date
    )

    if not valid:
        return False, message

    return True, ""


def run_chat_guardrails(question):

    valid, message = validate_question(
        question
    )

    if not valid:
        return False, message

    if detect_prompt_injection(
        question
    ):

        return (
            False,
            "Suspicious prompt detected."
        )

    return True, ""


def validate_weather_response(weather):

    if not weather:

        return (
            False,
            "Unable to retrieve weather information."
        )

    return (
        True,
        ""
    )