"""
DEMO 16

Why did RAG return this answer?
Trace the evidence.
"""

from search import search

question = (
    "How many annual leave days "
    "do full-time employees receive?"
)

results = search(
    question,
    top_k=3
)

print("QUESTION:")
print(question)

print(
    "\nRETRIEVAL EVIDENCE"
)

print(
    "(Lower distance = closer match)"
)

for rank, item in enumerate(
    results,
    start=1
):

    print("\n" + "=" * 60)

    print(
        f"Rank {rank}"
    )

    print(
        f"Document: "
        f"{item['source']}"
    )

    print(
        f"Distance: "
        f"{item['distance']:.4f}"
    )

    text = item["text"]

    preview = text[:250]

    print(
        "\nEvidence:"
    )

    print(preview)

print(
    "\nThe chunks above are the "
    "retrieval evidence used by RAG."
)