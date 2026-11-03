from pathlib import Path

import chromadb

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)

from llama_index.core.node_parser import (
    SentenceSplitter
)

from llama_index.core.embeddings import (
    BaseEmbedding
)

from llama_index.vector_stores.chroma import (
    ChromaVectorStore
)

from search import embed_text, DB_PATH
from ask_llm import ask_model

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

DOCUMENT_DIR = (
    Path(__file__).resolve().parent
    / "Document"
)

COLLECTION_NAME = "llamaindex_brightpath"

# ---------------------------------------------------
# REUSE EXISTING EMBEDDINGS
# ---------------------------------------------------

class LocalEmbedding(BaseEmbedding):

    def _get_text_embedding(self, text):
        return embed_text(text)

    async def _aget_text_embedding(self, text):
        return embed_text(text)

    def _get_query_embedding(self, query):
        return embed_text(query)

    async def _aget_query_embedding(self, query):
        return embed_text(query)

# ---------------------------------------------------
# STEP 1: READ DOCUMENTS
# ---------------------------------------------------

documents = SimpleDirectoryReader(
    input_dir=str(DOCUMENT_DIR)
).load_data()

print(
    f"Documents Loaded: {len(documents)}"
)

# ---------------------------------------------------
# STEP 2: CREATE NODES
# ---------------------------------------------------

splitter = SentenceSplitter(
    chunk_size=180,
    chunk_overlap=35
)

nodes = splitter.get_nodes_from_documents(
    documents
)

print(
    f"Nodes Created: {len(nodes)}"
)

print(
    "\nFirst Node Preview:"
)

print(
    nodes[0]
    .get_content()[:200]
)

# ---------------------------------------------------
# STEP 3: CHROMADB
# ---------------------------------------------------

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

try:
    client.delete_collection(
        COLLECTION_NAME
    )
except:
    pass

collection = (
    client.get_or_create_collection(
        COLLECTION_NAME
    )
)

vector_store = ChromaVectorStore(
    chroma_collection=collection
)

storage_context = (
    StorageContext.from_defaults(
        vector_store=vector_store
    )
)

# ---------------------------------------------------
# STEP 4: CREATE INDEX
# ---------------------------------------------------

index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
    embed_model=LocalEmbedding()
)

print(
    f"\nStored Nodes: "
    f"{collection.count()}"
)

# ---------------------------------------------------
# STEP 5: RETRIEVER
# ---------------------------------------------------

retriever = index.as_retriever(
    similarity_top_k=3
)

# ---------------------------------------------------
# STEP 6: QUESTION LOOP
# ---------------------------------------------------

while True:

    question = input(
        "\nQuestion (exit to stop): "
    ).strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    results = retriever.retrieve(
        question
    )

    context_parts = []

    print("\nRetrieved Nodes")

    for rank, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "=" * 60)

        print(
            "Rank:",
            rank
        )

        print(
            "Node ID:",
            result.node.node_id
        )

        print(
            "Score:",
            round(
                result.score,
                4
            )
        )

        text = (
            result.node.get_content()
        )

        print(
            "\nText:"
        )

        print(
            text[:300]
        )

        context_parts.append(
            text
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