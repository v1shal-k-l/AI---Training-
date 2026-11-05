import json
import gradio as gr

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

Return ONLY JSON.

Examples:

{
    "tool": "search_books",
    "keyword": "python"
}

{
    "tool": "reserve_book",
    "book_id": 101,
    "customer_name": "Ahmed"
}
"""


def process_message(message, history):

    try:

        # Let AI decide which tool to use
        tool_decision = ask_model(
            message,
            SYSTEM_PROMPT
        )

        action = json.loads(
            tool_decision
        )

        tool_name = action.get(
            "tool"
        )

        print(
            f"\n[TOOL SELECTED] {tool_name}"
        )

        if tool_name == "search_books":

            result = search_books(
                action["keyword"]
            )

        elif tool_name == "reserve_book":

            result = reserve_book(
                action["book_id"],
                action["customer_name"]
            )

        else:

            result = {
                "error":
                "Unknown tool selected"
            }

        final_answer = ask_model(
            question=f"""
User Request:
{message}

Tool Used:
{tool_name}

Tool Result:
{json.dumps(result, indent=2)}

Generate a user-friendly response.
""",
            context="""
You are a helpful library assistant.
Summarize the result clearly.
"""
        )

        return final_answer

    except Exception as ex:

        return f"❌ Error: {str(ex)}"


demo = gr.ChatInterface(
    fn=process_message,
    title="📚 Library AI Assistant",
    description="""
Ask about books, availability, or reservations.

Examples:
• Find books related to Python programming
• Is Python Crash Course available?
• Reserve Python Crash Course for Ahmed
• Show me books related to artificial intelligence
""",
    chatbot=gr.Chatbot(height=500),
    textbox=gr.Textbox(
        placeholder="Ask something...",
        container=False,
        scale=7
    )
)

demo.launch()