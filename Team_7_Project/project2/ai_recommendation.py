import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "meta-llama/llama-3.3-70b-instruct"
)


# Mock historical tickets
REFERENCE_TICKETS = [
    {
        "ticket_id": 101,
        "category": "Hardware",
        "priority": "Medium",
        "description": "Laptop overheating and shutting down frequently."
    },
    {
        "ticket_id": 102,
        "category": "Network",
        "priority": "High",
        "description": "VPN outage impacting multiple users."
    },
    {
        "ticket_id": 103,
        "category": "Software",
        "priority": "Critical",
        "description": "Payroll application unavailable across organization."
    },
    {
        "ticket_id": 104,
        "category": "Email",
        "priority": "Low",
        "description": "Email signature update request."
    }
]


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise Exception("JSON not found in model response")

    return json.loads(text[start:end + 1])


def analyze_ticket(ticket_message):

    prompt = f"""
You are an IT Helpdesk AI.

Use the historical tickets below as reference when assigning priority.

Historical Tickets:
{json.dumps(REFERENCE_TICKETS, indent=2)}

New Ticket:
{ticket_message}

Determine:
1. suggested_category
2. suggested_priority
3. troubleshooting_steps
4. explanation

Allowed Priorities:
- Low
- Medium
- High
- Critical

Return ONLY valid JSON.

{{
    "suggested_category": "",
    "suggested_priority": "",
    "troubleshooting_steps": "",
    "explanation": ""
}}
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1
        },
        timeout=60
    )

    response.raise_for_status()

    result = response.json()

    content = result["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except:
        return extract_json(content)


def generate_ai_suggestion(ticket_id, ticket_message):

    suggestion = analyze_ticket(ticket_message)

    ai_record = {
        "suggestion_id": 1,
        "ticket_id": ticket_id,
        "suggested_category": suggestion["suggested_category"],
        "suggested_priority": suggestion["suggested_priority"],
        "troubleshooting_steps": suggestion["troubleshooting_steps"],
        "explanation": suggestion["explanation"],
        "model_name": MODEL
    }

    return ai_record


def main():

    print("\n=== AI Ticket Analyzer ===\n")

    ticket_id = int(input("Enter Ticket ID: "))

    print("\nEnter Ticket Description:")
    ticket_message = input("> ")

    result = generate_ai_suggestion(
        ticket_id,
        ticket_message
    )

    print("\nGenerated ai_suggestions Record")
    print("=" * 60)

    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()