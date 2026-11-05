import json

from ask_llm import ask_model

from tools import (
    search_books,
    reserve_book
)


SYSTEM_PROMPT = """
You are a Library AI Assistant.

Available tools:

1. search_books(keyword)

2. reserve_book(book_id, customer_name)

Respond ONLY with JSON.

Search Example:

{
  "tool": "search_books",
  "keyword": "python"
}

Reservation Example:

{
  "tool": "reserve_book",
  "book_id": 101,
  "customer_name": "Ahmed"
}
"""


while True:

    question = input(
        "\nAsk: "
    )

    if question.lower() == "exit":
        break

    response = ask_model(
        question,
        SYSTEM_PROMPT
    )

    print(
        "\nLLM Decision:"
    )

    print(response)

    try:

        action = json.loads(
            response
        )

    except:

        print(
            "\nInvalid JSON returned."
        )

        continue

    tool = action.get("tool")

    print(
        "\nSelected Tool:",
        tool
    )

    if tool == "search_books":

        result = search_books(
            action["keyword"]
        )

    elif tool == "reserve_book":

        result = reserve_book(
            action["book_id"],
            action["customer_name"]
        )

    else:

        result = {
            "error":
                "Unknown tool"
        }

    print(
        "\nTool Result:"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    final_answer = ask_model(
        (
            f"User Question:\n"
            f"{question}\n\n"
            f"Tool Result:\n"
            f"{json.dumps(result)}\n\n"
            f"Provide a user-friendly answer."
        ),
        "You are a helpful library assistant."
    )

    print(
        "\nAssistant:"
    )

    print(final_answer)