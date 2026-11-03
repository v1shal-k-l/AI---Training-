from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from search import embed_text, DB_PATH
from ask_llm import ask_model

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

DOCUMENT_DIR = Path(__file__).resolve().parent / "Document"

COLLECTION_NAME = "langchain_brightpath"


# ---------------------------------------------------
# LOCAL EMBEDDINGS WRAPPER
# ---------------------------------------------------

class LocalEmbeddings(Embeddings):

    def embed_documents(self, texts):

        embeddings = []

        for text in texts:
            embeddings.append(
                embed_text(text)
            )

        return embeddings

    def embed_query(self, text):

        return embed_text(text)


# ---------------------------------------------------
# STEP 1: LOAD DOCUMENTS
# ---------------------------------------------------

documents = []

for file_path in DOCUMENT_DIR.glob("*.txt"):

    text = file_path.read_text(
        encoding="utf-8"
    )

    documents.append(
        Document(
            page_content=text,
            metadata={
                "source": file_path.name
            }
        )
    )

print(f"Documents Loaded: {len(documents)}")

if not documents:
    raise Exception(
        "No .txt files found inside Document folder."
    )


# ---------------------------------------------------
# STEP 2: CHUNK DOCUMENTS
# ---------------------------------------------------

splitter = (
    RecursiveCharacterTextSplitter
    .from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=180,
        chunk_overlap=35
    )
)

chunks = splitter.split_documents(
    documents
)

for index, chunk in enumerate(
    chunks,
    start=1
):
    chunk.metadata[
        "chunk_id"
    ] = f"lc_chunk_{index:03d}"

print(f"Chunks Created: {len(chunks)}")

print("\nFirst Chunk Preview:")
print(
    chunks[0].page_content[:150]
)


# ---------------------------------------------------
# STEP 3: CREATE VECTOR STORE
# ---------------------------------------------------

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=LocalEmbeddings(),
    collection_name=COLLECTION_NAME,
    persist_directory=str(DB_PATH)
)

print(
    "\nLangChain Vector Store Created."
)


# ---------------------------------------------------
# STEP 4: QUESTION LOOP
# ---------------------------------------------------

while True:

    question = input(
        "\nAsk a question (exit to quit): "
    ).strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    results = (
        vector_store
        .similarity_search_with_score(
            question,
            k=3
        )
    )

    context_parts = []

    print("\nRetrieved Chunks")

    for document, distance in results:

        print("\n" + "-" * 60)

        print(
            "Chunk ID:",
            document.metadata.get(
                "chunk_id",
                "N/A"
            )
        )

        print(
            "Source:",
            document.metadata.get(
                "source",
                "N/A"
            )
        )

        print(
            "Distance:",
            round(distance, 4)
        )

        print("\nText Preview:")
        print(
            document.page_content[:300]
        )

        context_parts.append(
            f"""
SOURCE:
{document.metadata.get('source', 'Unknown')}

CONTENT:
{document.page_content}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    print(
        "\nGenerating Answer..."
    )

    answer = ask_model(
        question,
        context
    )

    print("\n" + "=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)
    print(answer)