from pathlib import Path

import chromadb
import tiktoken
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# =====================================================
# CONFIGURATION
# =====================================================

PROJECT_DIR = Path(__file__).resolve().parent
DOCUMENT_DIR = PROJECT_DIR / "Document"

DB_PATH = PROJECT_DIR / "chroma_db"
COLLECTION_NAME = "company_documents"

TOKENIZER = tiktoken.get_encoding("cl100k_base")


# =====================================================
# TASK 1
# READ + TOKENIZE
# =====================================================

def read_documents():

    documents = []

    print("\n" + "=" * 70)
    print("TASK 1 : READ AND TOKENIZE DOCUMENTS")
    print("=" * 70)

    for file_path in DOCUMENT_DIR.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        token_count = len(
            TOKENIZER.encode(text)
        )

        print(f"\nFile Name : {file_path.name}")
        print(f"Characters : {len(text)}")
        print(f"Token Count : {token_count}")

        print("\nDocument Preview:")
        print("-" * 50)
        print(text[:300])

        documents.append({
            "filename": file_path.name,
            "text": text
        })

    return documents


# =====================================================
# TASK 2
# CHUNKING
# =====================================================

def make_chunks(text,
                chunk_size=120,
                overlap=20):

    tokens = TOKENIZER.encode(text)

    chunks = []

    start = 0

    while start < len(tokens):

        end = min(
            start + chunk_size,
            len(tokens)
        )

        chunk = TOKENIZER.decode(
            tokens[start:end]
        )

        chunks.append(chunk)

        if end == len(tokens):
            break

        start = end - overlap

    return chunks


# =====================================================
# EMBEDDING FUNCTION
# all-MiniLM-L6-v2
# =====================================================

def embed_texts(texts):

    embedder = DefaultEmbeddingFunction()

    vectors = embedder(texts)

    return [
        vector.tolist()
        if hasattr(vector, "tolist")
        else list(vector)
        for vector in vectors
    ]


# =====================================================
# TASK 2
# CHUNK + EMBED
# =====================================================

def process_documents(documents):

    print("\n" + "=" * 70)
    print("TASK 2 : CHUNKING & EMBEDDINGS")
    print("=" * 70)

    all_chunks = []

    for document in documents:

        filename = document["filename"]
        text = document["text"]

        chunks = make_chunks(
            text,
            chunk_size=120,
            overlap=20
        )

        print(f"\nFile : {filename}")
        print(f"Chunk Count : {len(chunks)}")

        print("\nSample Chunk:")
        print("-" * 50)
        print(chunks[0][:500])

        embeddings = embed_texts(chunks)

        print(
            "\nEmbedding Vector Size:",
            len(embeddings[0])
        )

        for index, chunk in enumerate(chunks):

            all_chunks.append({
                "id": f"{filename}_{index}",
                "text": chunk,
                "source": filename,
                "embedding": embeddings[index]
            })

    return all_chunks


# =====================================================
# TASK 3
# CHROMADB
# =====================================================

def create_database():

    client = chromadb.PersistentClient(
        path=str(DB_PATH)
    )

    return client


def store_chunks(all_chunks):

    print("\n" + "=" * 70)
    print("TASK 3 : STORE IN CHROMADB")
    print("=" * 70)

    client = create_database()

    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        embedding_function=None
    )

    collection.add(
        ids=[
            chunk["id"]
            for chunk in all_chunks
        ],

        documents=[
            chunk["text"]
            for chunk in all_chunks
        ],

        embeddings=[
            chunk["embedding"]
            for chunk in all_chunks
        ],

        metadatas=[
            {"source": chunk["source"]}
            for chunk in all_chunks
        ]
    )

    print(
        f"\nStored {collection.count()} chunks."
    )

    return collection


# =====================================================
# SEARCH
# =====================================================

def search_question(collection):

    print("\n" + "=" * 70)
    print("SEARCH DOCUMENTS")
    print("=" * 70)

    question = input(
        "\nEnter your question: "
    )

    question_embedding = embed_texts(
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            question_embedding
        ],
        n_results=2,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    print("\nTop 2 Results")
    print("=" * 70)

    for i in range(
            len(results["documents"][0])):

        document = \
            results["documents"][0][i]

        source = \
            results["metadatas"][0][i]["source"]

        distance = \
            results["distances"][0][i]

        print(f"\nResult #{i + 1}")

        print(
            f"Source File : {source}"
        )

        print(
            f"Cosine Distance : "
            f"{round(distance, 4)}"
        )

        print("\nChunk:")
        print("-" * 50)
        print(document[:600])


# =====================================================
# MAIN
# =====================================================

def main():

    documents = read_documents()

    all_chunks = process_documents(
        documents
    )

    collection = store_chunks(
        all_chunks
    )

    search_question(collection)


if __name__ == "__main__":
    main()