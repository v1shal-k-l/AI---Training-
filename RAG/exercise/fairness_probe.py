"""
DEMO 17

Simple Retrieval Consistency Check
"""

from search import search

questions = [

    "How many annual leave days "
    "does a full-time male employee receive?",

    "How many annual leave days "
    "does a full-time female employee receive?",

    "How many annual leave days "
    "does a full-time employee receive?"

]

print(
    "FAIRNESS / CONSISTENCY PROBE"
)

print(
    "\nSame policy, "
    "different wording.\n"
)

for question in questions:

    results = search(
        question,
        top_k=3
    )

    matched_chunks = [

        item["source"]

        for item in results

        if "18 days"
        in item["text"].lower()

    ]

    print(
        "Question:",
        question
    )

    print(
        "Top Match:",
        results[0]["source"]
    )

    print(
        "Distance:",
        round(
            results[0]["distance"],
            4
        )
    )

    print(
        "Evidence with "
        "'18 days':",
        matched_chunks
        if matched_chunks
        else "NOT FOUND"
    )

    print("-" * 60)

print(
    "\nDiscussion:"
)

print(
    "Did all three questions retrieve "
    "the same leave-policy evidence?"
)

print(
    "This checks retrieval consistency,"
)

print(
    "not overall LLM fairness."
)