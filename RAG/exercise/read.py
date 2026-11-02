from pathlib import Path
import tiktoken

DOCUMENT_FOLDER = Path("Document")

# Tokenizer
encoding = tiktoken.get_encoding("cl100k_base")

print("\nFILES FOUND:")
print("-" * 50)

for file_path in DOCUMENT_FOLDER.iterdir():

    # Skip folders
    if not file_path.is_file():
        continue

    print(f"\nFile: {file_path.name}")

    try:
        # Read as text
        text = file_path.read_text(encoding="utf-8")

        # Tokenize
        tokens = encoding.encode(text)

        print(f"Characters: {len(text)}")
        print(f"Tokens: {len(tokens)}")

        print("\nFirst 300 Characters:")
        print(text[:300])

    except Exception as e:
        print(f"Could not read file: {e}")
