
"""
03_embeddings_demo.py

Generate embeddings from user-provided sentences and
compare semantic similarity.
"""

from math import sqrt

from rag_core import embed_texts


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""

    dot = sum(x * y for x, y in zip(a, b))

    length_a = sqrt(sum(x * x for x in a))
    length_b = sqrt(sum(y * y for y in b))

    return dot / (length_a * length_b)


print("=" * 60)
print("Embedding Demo - all-MiniLM-L6-v2")
print("=" * 60)

print("\nEnter 3 sentences:\n")

sentences = []

for i in range(1, 4):
    sentence = input(f"Sentence {i}: ").strip()
    sentences.append(sentence)

# Generate embeddings
vectors = embed_texts(sentences)

print("\n")
print("=" * 60)
print("Embeddings are arrays of numbers representing meaning.")
print("=" * 60)

for sentence, vector in zip(sentences, vectors):
    print("\nText:")
    print(sentence)

    print(f"Vector Dimension: {len(vector)}")

    print(
        "First 8 Vector Values:",
        [round(x, 4) for x in vector[:8]]
    )

print("\n")
print("=" * 60)
print("Semantic Similarity")
print("=" * 60)

similarity_1_2 = cosine_similarity(vectors[0], vectors[1])
similarity_1_3 = cosine_similarity(vectors[0], vectors[2])

print(
    f"Sentence 1 ↔ Sentence 2: {round(similarity_1_2, 3)}"
)

print(
    f"Sentence 1 ↔ Sentence 3: {round(similarity_1_3, 3)}"
)

print(
    "\nHigher score = more similar meaning."
)

print(
    "\nThe model runs locally. First use may download "
    "the model (~80 MB)."
)