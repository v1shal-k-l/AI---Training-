import chromadb
from pathlib import Path

from chromadb.utils.embedding_functions import (
    DefaultEmbeddingFunction
)

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

DB_PATH = PROJECT_DIR / "chroma_db"

COLLECTION_NAME = "company_documents"

# ---------------------------------------------------
# EMBEDDING MODEL
# ---------------------------------------------------

embedding_model = DefaultEmbeddingFunction()


def embed_text(text):
    """
    Convert question into embedding vector.
    """

    vector = embedding_model([text])[0]

    if hasattr(vector, "tolist"):
        vector = vector.tolist()

    return vector


# ---------------------------------------------------
# LOAD COLLECTION
# ---------------------------------------------------

def get_collection():

    client = chromadb.PersistentClient(
        path=str(DB_PATH)
    )

    return client.get_collection(
        COLLECTION_NAME
    )


# ---------------------------------------------------
# SEARCH FUNCTION
# ---------------------------------------------------

def search(question, top_k=3):

    collection = get_collection()

    question_embedding = embed_text(
        question
    )

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    matches = []

    for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
    ):

        matches.append({
            "source": metadata["source"],
            "text": doc,
            "distance": distance
        })

    return matches


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":

    question = input(
        "\nAsk a question: "
    )

    matches = search(question)

    print("\nTop Matches\n")

    for i, match in enumerate(
            matches,
            start=1
    ):

        print("-" * 70)

        print(f"Rank: {i}")
        print(f"Source: {match['source']}")

        print(
            f"Distance: "
            f"{round(match['distance'], 4)}"
        )

        print("\nChunk:")

        print(match["text"])