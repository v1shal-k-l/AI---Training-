"""
RAG + OpenRouter
"""
import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

if not API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env file"
    )

def ask_model(question, context):

    prompt = f"""
You are a document assistant.

Answer ONLY from the supplied context.

If the answer is not found in the context, reply:
"The documents do not contain that information."

Context:
{context}

Question:
{question}

Answer:
"""

    try:

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
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
                "temperature": 0.3
            },
            timeout=60
        )

        print(
            f"\nOpenRouter Status: "
            f"{response.status_code}"
        )

        if response.status_code != 200:
            print("\nError Response:")
            print(response.text)
            return "OpenRouter request failed."

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------------------------------------------
# TEST
# ---------------------------------------------------

if __name__ == "__main__":

    context = """
Employees receive 20 days of annual leave.
Employees can carry forward up to 5 unused days.
"""

    question = "How many leave days are allowed?"

    answer = ask_model(
        question,
        context
    )

    print("\nAnswer:")
    print(answer)