import json

from ask_llm import ask_model

from tools import (
    list_all_workshops,
    find_cheapest_workshop,
    search_workshops,
    calculate_workshop_fee,
    apply_coupon
)

from guardrails import (
    validate_length,
    contains_pii,
    detect_prompt_injection,
    detect_sql_injection,
    detect_xss,
    is_workshop_question,
    validate_tool,
    validate_participants,
    validate_coupon,
    output_contains_sensitive_data,
    RateLimiter,
    REFUSAL_MESSAGE
)

# ---------------------------------------------------
# MEMORY
# ---------------------------------------------------

conversation_history = []

# ---------------------------------------------------
# RATE LIMITER
# ---------------------------------------------------

limiter = RateLimiter(limit=25)

# ---------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------

SYSTEM_PROMPT = """
You are a Workshop AI Agent.

AVAILABLE TOOLS:

1. list_all_workshops

Example:
{
    "tool":"list_all_workshops"
}

2. find_cheapest_workshop

Example:
{
    "tool":"find_cheapest_workshop"
}

3. search_workshops

Example:
{
    "tool":"search_workshops",
    "keyword":"python"
}

4. calculate_workshop_fee

Example:
{
    "tool":"calculate_workshop_fee",
    "workshop_id":"W101",
    "participants":5
}

5. apply_coupon

Example:
{
    "tool":"apply_coupon",
    "workshop_id":"W101",
    "participants":5,
    "coupon_code":"WELCOME10"
}

RULES:

1. Reply ONLY with JSON.
2. Do not explain.
3. Do not use markdown.
4. Never invent workshop IDs.
5. Never invent coupon codes.
6. Use available tools only.
7. Use conversation history when needed.
"""

# ---------------------------------------------------
# TOOL EXECUTION
# ---------------------------------------------------

def execute_tool(action):

    tool = action["tool"]

    print(
        f"\n[AGENT CHOSE TOOL] {tool}"
    )

    if tool == "list_all_workshops":

        return list_all_workshops.invoke({})

    if tool == "find_cheapest_workshop":

        return find_cheapest_workshop.invoke({})

    if tool == "search_workshops":

        return search_workshops.invoke(
            {
                "keyword":
                    action["keyword"]
            }
        )

    if tool == "calculate_workshop_fee":

        return calculate_workshop_fee.invoke(
            {
                "workshop_id":
                    action["workshop_id"],

                "participants":
                    action["participants"]
            }
        )

    if tool == "apply_coupon":

        return apply_coupon.invoke(
            {
                "workshop_id":
                    action["workshop_id"],

                "participants":
                    action["participants"],

                "coupon_code":
                    action["coupon_code"]
            }
        )

    return "Unknown tool"


# ---------------------------------------------------
# AGENT LOOP
# ---------------------------------------------------

print("\nWorkshop Agentic AI Started")
print("Type 'exit' to quit")

while True:

    question = input(
        "\nYou: "
    ).strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    # --------------------------
    # RATE LIMIT
    # --------------------------

    if not limiter.allow():

        print(
            "\nAgent: Session request limit exceeded."
        )

        break

    # --------------------------
    # LENGTH CHECK
    # --------------------------

    if not validate_length(question):

        print(
            "\nAgent: Input exceeds maximum length."
        )

        continue

    # --------------------------
    # PII CHECK
    # --------------------------

    if contains_pii(question):

        print(
            "\nAgent: Please do not share personal or sensitive information."
        )

        continue

    # --------------------------
    # PROMPT INJECTION
    # --------------------------

    if detect_prompt_injection(question):

        print(
            "\nAgent: Request blocked due to security policy."
        )

        continue

    # --------------------------
    # SQL INJECTION
    # --------------------------

    if detect_sql_injection(question):

        print(
            "\nAgent: Suspicious input detected."
        )

        continue

    # --------------------------
    # XSS DETECTION
    # --------------------------

    if detect_xss(question):

        print(
            "\nAgent: Invalid input detected."
        )

        continue

    # --------------------------
    # DOMAIN RESTRICTION
    # --------------------------

    if not is_workshop_question(question):

        print(
            f"\nAgent: {REFUSAL_MESSAGE}"
        )

        continue

    try:

        # --------------------------
        # BUILD MEMORY CONTEXT
        # --------------------------

        memory_context = "\n".join(
            conversation_history[-10:]
        )

        ai_question = f"""
Conversation History:

{memory_context}

Current Question:

{question}
"""

        # --------------------------
        # TOOL DECISION
        # --------------------------

        decision = ask_model(
            ai_question,
            SYSTEM_PROMPT
        )

        print(
            "\n[RAW AGENT DECISION]"
        )

        print(decision)

        action = json.loads(
            decision
        )

        # --------------------------
        # TOOL VALIDATION
        # --------------------------

        if not validate_tool(
                action["tool"]):

            print(
                "\nAgent: Unauthorized tool selection."
            )

            continue

        # --------------------------
        # PARTICIPANT VALIDATION
        # --------------------------

        if action["tool"] in [
            "calculate_workshop_fee",
            "apply_coupon"
        ]:

            if not validate_participants(
                    action["participants"]
            ):

                print(
                    "\nAgent: Participant count must be between 1 and 100."
                )

                continue

        # --------------------------
        # COUPON VALIDATION
        # --------------------------

        if action["tool"] == "apply_coupon":

            if not validate_coupon(
                    action["coupon_code"]
            ):

                print(
                    "\nAgent: Invalid coupon code."
                )

                continue

        # --------------------------
        # EXECUTE TOOL
        # --------------------------

        tool_result = execute_tool(
            action
        )

        print(
            "\n[TOOL RESULT]"
        )

        print(tool_result)

        # --------------------------
        # GENERATE FINAL RESPONSE
        # --------------------------

        final_response = ask_model(
            question=f"""
User Question:
{question}

Tool Result:
{tool_result}
""",
            context="""
You are a Workshop Assistant.

RULES:

1. Answer ONLY using tool output.
2. Never invent workshops.
3. Never invent discounts.
4. Never invent coupon codes.
5. Never invent pricing.
6. If tool output lacks information,
   say you do not have verified information.
"""
        )

        # --------------------------
        # OUTPUT GUARDRAIL
        # --------------------------

        if output_contains_sensitive_data(
                final_response):

            print(
                "\nAgent: Response blocked for security reasons."
            )

            continue

        print(
            "\nAgent:"
        )

        print(final_response)

        # --------------------------
        # UPDATE MEMORY
        # --------------------------

        conversation_history.append(
            f"User: {question}"
        )

        conversation_history.append(
            f"Agent: {final_response}"
        )

    except Exception as error:

        print(
            "\nAgent Error:",
            error
        )