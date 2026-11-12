import os
import json
import requests

from dotenv import load_dotenv

from tools import (
    search_restaurants,
    calculate_dining_cost
)

from guardrails import (
    validate_input,
    is_restaurant_question,
    detect_pii,
    redact_pii,
    detect_prompt_injection,
    valid_guest_count,
    unsafe_output,
    REFUSAL_MESSAGE
)

# --------------------------------------------------
# ENV
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

if not API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY not found in .env"
    )

# --------------------------------------------------
# MEMORY
# --------------------------------------------------

conversation_history = []

# --------------------------------------------------
# TOOL SELECTION PROMPT
# --------------------------------------------------

TOOL_SELECTION_PROMPT = """
You are a Restaurant Reservation Assistant.

You can use ONLY these tools:

1. search_restaurants

Example:

{
    "tool": "search_restaurants",
    "keyword": "indian"
}

2. calculate_dining_cost

Example:

{
    "tool": "calculate_dining_cost",
    "restaurant_id": "R101",
    "guests": 4
}

RULES:

1. Reply ONLY with valid JSON.
2. No markdown.
3. No explanations.
4. Use conversation history.
5. If user says:
   - "Make that 6 people"
   - "Increase it to 6 people"
   - "For 6 people"

   then use the restaurant discussed previously.

6. Never invent restaurant IDs.
7. Never invent restaurant names.
8. Never invent prices.
"""

# --------------------------------------------------
# OPENROUTER CALL
# --------------------------------------------------

def ask_openrouter(question, context):

    prompt = f"""
Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
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
            "temperature": 0
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]

# --------------------------------------------------
# TOOL EXECUTION
# --------------------------------------------------

def execute_tool(action):

    tool = action["tool"]

    print(f"\n[TOOL SELECTED] {tool}")
    print(f"[TOOL ARGS] {action}")

    if tool == "search_restaurants":

        return search_restaurants(
            action["keyword"]
        )

    if tool == "calculate_dining_cost":

        guests = action["guests"]

        if not valid_guest_count(
            guests
        ):
            return {
                "error":
                "Guest count must be between 1 and 20."
            }

        return calculate_dining_cost(
            action["restaurant_id"],
            guests
        )

    return {
        "error":
        "Unknown tool selected."
    }

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

print("\nRestaurant AI Assistant")
print("Commands:")
print("  /new  -> Start a new conversation")
print("  exit  -> Quit")

while True:

    question = input(
        "\nYou: "
    ).strip()

    if question.lower() == "exit":
        break

    # ----------------------------
    # START NEW CHAT
    # ----------------------------

    if question.lower() == "/new":

        conversation_history.clear()

        print(
            "\n✅ New conversation started."
        )

        continue

    # ----------------------------
    # GUARDRAILS
    # ----------------------------

    if not validate_input(question):

        print(
            "\nAgent: Invalid input."
        )

        continue

    if detect_pii(question):

        print(
            "\nAgent: Please do not share email addresses or phone numbers."
        )

        continue

    if detect_prompt_injection(question):

        print(
            "\nAgent: Request blocked by security policy."
        )

        continue

    if not is_restaurant_question(question):

        print(
            f"\nAgent: {REFUSAL_MESSAGE}"
        )

        continue

    try:

        # ----------------------------
        # MEMORY CONTEXT
        # ----------------------------

        memory_context = "\n".join(
            conversation_history[-10:]
        )

        # ----------------------------
        # TOOL DECISION
        # ----------------------------

        tool_decision = ask_openrouter(
            question,
            TOOL_SELECTION_PROMPT
            + "\n\nConversation History:\n"
            + memory_context
        )

        print(
            "\n[RAW TOOL DECISION]"
        )

        print(tool_decision)

        action = json.loads(
            tool_decision
        )

        # ----------------------------
        # EXECUTE TOOL
        # ----------------------------

        tool_result = execute_tool(
            action
        )

        print(
            "\n[TOOL RESULT]"
        )

        print(
            json.dumps(
                tool_result,
                indent=2
            )
        )

        # ----------------------------
        # FINAL RESPONSE
        # ----------------------------

        final_answer = ask_openrouter(
            question,
            f"""
You are a Restaurant Assistant.

Answer ONLY using the tool result.

Tool Result:

{json.dumps(tool_result, indent=2)}

RULES:

1. Never invent restaurant names.
2. Never invent prices.
3. Never invent availability.
4. Be concise.
"""
        )

        final_answer = redact_pii(
            final_answer
        )

        if unsafe_output(
            final_answer
        ):

            print(
                "\nAgent: Response blocked by security policy."
            )

            continue

        print(
            "\nAgent:"
        )

        print(final_answer)

        # ----------------------------
        # SAVE MEMORY
        # ----------------------------

        conversation_history.append(
            f"User: {question}"
        )

        conversation_history.append(
            f"Agent: {final_answer}"
        )

    except Exception as exc:

        print(
            "\nAgent Error:"
        )

        print(exc)