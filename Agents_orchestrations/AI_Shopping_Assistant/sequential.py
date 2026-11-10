import asyncio
import re

from agent import (
    InventoryAgent,
    PricingAgent,
    RecommendationAgent
)

from guardrails import (
    validate_input,
    contains_pii,
    redact_pii,
    detect_prompt_injection
)


VALID_CATEGORIES = {
    "laptop",
    "smartphone",
    "tablet",
    "monitor",
    "headphone",
    "printer"
}


class SequentialBuilder:

    def __init__(self):
        self.agents = []

    def add_agent(self, agent):

        self.agents.append(agent)

        return self

    def build(self):

        return SequentialWorkflow(
            self.agents
        )


class SequentialWorkflow:

    def __init__(self, agents):

        self.agents = agents

    async def run(self, context):

        for agent in self.agents:

            context = await agent.run(
                context
            )

        return context


def parse_request(text):

    text_lower = text.lower()

    category_match = re.search(
        r"(laptop|smartphone|tablet|monitor|headphone|printer)s?",
        text_lower
    )

    category = (
        category_match.group(1)
        if category_match
        else None
    )

    quantity_match = re.search(
        r"(\d+)\s+"
        r"(?:laptops?|smartphones?|tablets?|"
        r"monitors?|headphones?|printers?)",
        text_lower
    )

    quantity = (
        int(quantity_match.group(1))
        if quantity_match
        else 1
    )

    budget_match = re.search(
        r"₹\s*([\d,]+)",
        text
    )

    if budget_match:

        budget = int(
            budget_match.group(1)
            .replace(",", "")
        )

    else:

        budget = 999999999

    return {

        "category":
            category,

        "quantity":
            quantity,

        "budget":
            budget
    }


def is_shopping_request(context):

    return (
        context["category"]
        in VALID_CATEGORIES
    )


async def main():

    print(
        "\n🛍️ E-Commerce Multi-Agent Shopping Assistant"
    )

    print(
        "Type 'exit' to quit.\n"
    )

    while True:

        request = input(
            "Customer Request: "
        ).strip()

        if request.lower() == "exit":
            break

        # ----------------------------
        # INPUT VALIDATION
        # ----------------------------

        if not validate_input(
            request
        ):

            print("""
🤖 Shopping Assistant:

I couldn't understand your request.

Examples:

• Recommend 2 laptops within ₹120000
• Find 3 smartphones under ₹100000
• Recommend 2 monitors under ₹50000
""")
            continue

        # ----------------------------
        # PII DETECTION
        # ----------------------------

        if contains_pii(
            request
        ):

            print("""
🤖 Shopping Assistant:

For your privacy, please do not share:

• Email addresses
• Phone numbers
• Personal contact details

Please ask your shopping question again.
""")
            continue

        # ----------------------------
        # PROMPT INJECTION
        # ----------------------------

        if detect_prompt_injection(
            request
        ):

            print("""
🤖 Shopping Assistant:

I cannot process requests attempting to override system instructions.

Please ask a shopping-related question.
""")
            continue

        context = parse_request(
            request
        )

        # ----------------------------
        # DOMAIN GUARDRAIL
        # ----------------------------

        if not is_shopping_request(
            context
        ):

            print("""
🤖 Shopping Assistant:

I can help only with product shopping requests.

Supported categories:

• Laptops
• Smartphones
• Tablets
• Monitors
• Headphones
• Printers

Example requests:

• Recommend 2 laptops within ₹120000 total
• Find 3 smartphones under ₹100000
• Recommend 2 monitors under ₹50000
""")

            continue

        print(
            f"\n📦 Category: {context['category']}"
        )

        print(
            f"🛒 Quantity: {context['quantity']}"
        )

        print(
            f"💰 Budget: ₹{context['budget']:,}"
        )

        workflow = (

            SequentialBuilder()

            .add_agent(
                InventoryAgent()
            )

            .add_agent(
                PricingAgent()
            )

            .add_agent(
                RecommendationAgent()
            )

            .build()
        )

        try:

            result = await workflow.run(
                context
            )

            print(
                "\n" + "=" * 70
            )

            print(
                redact_pii(
                    result["recommendation"]
                )
            )

            print(
                "=" * 70
            )

        except Exception as error:

            print("""
🤖 Shopping Assistant:

An unexpected error occurred while processing your request.
""")

            print(error)


if __name__ == "__main__":

    asyncio.run(main())