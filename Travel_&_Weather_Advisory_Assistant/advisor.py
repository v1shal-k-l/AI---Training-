import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv(
        "OPENROUTER_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv(
        "OPENROUTER_API_KEY"
    ),
    temperature=0.3
)


def generate_advice(
    trip_details,
    weather,
    question
):
    prompt = f"""
You are a friendly AI Travel & Weather Advisory Assistant.

Respond directly to the employee in a conversational manner.

Rules:
- Do not return JSON.
- Do not use markdown.
- Do not use numbered lists.
- Sound like a helpful chatbot.
- Keep the response under 150 words.
- Provide weather summary.
- Provide travel recommendation.
- Provide 3-4 packing suggestions.

Trip Details:
{trip_details}

Weather Details:
{weather}

Employee Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content