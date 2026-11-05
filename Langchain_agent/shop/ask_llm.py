import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

if not API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env"
    )


def ask_model(question, context):

    prompt = f"""
{context}

User Question:
{question}

Answer:
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]