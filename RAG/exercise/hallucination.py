"""
DEMO 15

Supported vs Unsupported Answers

Run:
python 15_hallucination_test.py

AI Version:
python 15_hallucination_test.py --ai
"""

import argparse

from search import search
from ask_llm import ask_model

TESTS = [
    {
        "question":
            "How many annual leave days do full-time employees receive?",
        "expected":
            "18 days"
    },
    {
        "question":
            "What is the annual travel allowance in rupees?",
        "expected":
            None
    }
]

parser = argparse.ArgumentParser()

parser.add_argument(
    "--ai",
    action="store_true"
)

args = parser.parse_args()

for test in TESTS:

    question = test["question"]

    results = search(
        question,
        top_k=3
    )

    context = "\n\n".join(
        result["text"]
        for result in results
    )

    print("\n" + "=" * 75)
    print("QUESTION:", question)

    print("\nTOP RETRIEVED CHUNKS")

    for item in results:

        print(
            f"- {item['source']} "
            f"(distance={item['distance']:.4f})"
        )

    if test["expected"]:

        found = (
            test["expected"].lower()
            in context.lower()
        )

        print(
            "\nExpected Evidence Found:",
            found
        )

    else:

        print(
            "\nExpected Evidence: NONE"
        )

        print(
            "Retriever may still return "
            "similar chunks."
        )

    if args.ai:

        answer = ask_model(
            question,
            context
        )

        print("\nAI ANSWER")
        print("-" * 50)
        print(answer)

print(
    "\nKey Idea:"
)

print(
    "Low cosine distance does not "
    "guarantee that the answer "
    "actually exists in the documents."
)