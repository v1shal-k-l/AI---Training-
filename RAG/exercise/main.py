from rag_pr import (
    read_documents,
    process_documents,
    store_chunks
)

from ask_llm import ask_model

# ---------------------------------------------------
# BUILD DATABASE
# ---------------------------------------------------

documents = read_documents()

all_chunks = process_documents(
    documents
)

store_chunks(all_chunks)

# Import AFTER database creation
from search import search

# ---------------------------------------------------
# QUESTION LOOP
# ---------------------------------------------------

while True:

    question = input(
        "\nAsk a question ('exit' to quit): "
    )

    if question.lower() == "exit":
        break

    matches = search(
        question,
        top_k=3
    )

    context = "\n\n".join(
        chunk["text"]
        for chunk in matches
    )

    print("\nGenerating Answer...\n")

    answer = ask_model(
        question,
        context
    )

    print("\n" + "=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)

    print(answer)