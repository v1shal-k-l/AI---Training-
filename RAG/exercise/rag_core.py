"""Shared, beginner-friendly RAG functions. Read this file after steps 1–4."""

from pathlib import Path

import chromadb
import tiktoken
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENT_DIR = PROJECT_DIR / "Document"

DB_PATH = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "company_documents"

# -------------------------------------------------------------------
# Tokenizer
# -------------------------------------------------------------------

TOKENIZER = tiktoken.get_encoding("cl100k_base")

# -------------------------------------------------------------------
# Read Documents
# -------------------------------------------------------------------


def read_document():
    """
    Load all .txt files from the Document folder
    and combine them into a single text corpus.
    """

    all_text = []

    print("\nLoading Documents...")
    print("-" * 50)

    for file_path in DOCUMENT_DIR.glob("*.txt"):

        print(f"Loaded: {file_path.name}")

        text = file_path.read_text(encoding="utf-8")

        token_count = len(TOKENIZER.encode(text))

        print(f"  Characters: {len(text)}")
        print(f"  Tokens: {token_count}")

        all_text.append(
            f"\n\n===== {file_path.name} =====\n\n{text}"
        )

    combined_text = "\n".join(all_text)

    print("\nSummary")
    print("-" * 50)
    print("Total Characters:", len(combined_text))
    print("Total Tokens:", len(TOKENIZER.encode(combined_text)))

    return combined_text


# -------------------------------------------------------------------
# Chunking
# -------------------------------------------------------------------


def make_chunks(text, chunk_size=180, overlap=35):
    """
    Split text into overlapping token chunks.
    """

    if not (0 <= overlap < chunk_size):
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    token_ids = TOKENIZER.encode(text)

    chunks = []
    start = 0

    while start < len(token_ids):

        end = min(start + chunk_size, len(token_ids))

        chunk = TOKENIZER.decode(
            token_ids[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(token_ids):
            break

        start = end - overlap

    return chunks


# -------------------------------------------------------------------
# Embeddings
# -------------------------------------------------------------------


def embed_texts(texts):
    """
    Convert text into embedding vectors.
    """

    model = DefaultEmbeddingFunction()

    vectors = model(texts)

    return [
        v.tolist() if hasattr(v, "tolist")
        else list(v)
        for v in vectors
    ]


# -------------------------------------------------------------------
# Chroma DB
# -------------------------------------------------------------------


def get_database():
    """
    Open Chroma persistent database.
    """

    return chromadb.PersistentClient(
        path=str(DB_PATH)
    )


# -------------------------------------------------------------------
# Search
# -------------------------------------------------------------------


def search_chunks(question, top_k=3):
    """
    Search the vector database.
    """

    db = get_database()

    try:
        collection = db.get_collection(
            COLLECTION_NAME,
            embedding_function=None,
        )

    except Exception as exc:
        raise RuntimeError(
            "No indexed collection. Run 05_store_in_chroma.py first."
        ) from exc

    count = collection.count()

    if count == 0:
        raise RuntimeError(
            "The collection is empty. Run 05_store_in_chroma.py first."
        )

    question_vector = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=min(top_k, count),
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    matches = []

    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append(
            {
                "id": chunk_id,
                "text": text,
                "source": metadata.get(
                    "source",
                    "unknown",
                ),
                "distance": distance,
            }
        )

    return matches


# -------------------------------------------------------------------
# Test
# -------------------------------------------------------------------

if __name__ == "__main__":

    text = read_document()

    print("\nFirst 700 Characters\n")
    print(text[:700])