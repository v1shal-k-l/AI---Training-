import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# 1. Open the scanned PDF using PyMuPDF
pdf_path = "EY_Scanned_PDF_OCR_Practice.pdf"
doc = fitz.open(pdf_path)

all_text = ""

# Process each page
for page_num in range(len(doc)):
    page = doc[page_num]

    # 2. Convert the PDF page into an image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_path = f"page_{page_num + 1}.png"
    pix.save(image_path)

    # Open image with PIL
    img = Image.open(image_path)

    # 3. Run Tesseract OCR on the image
    text = pytesseract.image_to_string(img)

    all_text += text + "\n"

# 4. Print the extracted text
print("=== OCR EXTRACTED TEXT ===")
print(all_text)

# 5. Check whether Forklift FL-17 was detected
if "Forklift FL-17" in all_text:
    print("\n✓ Forklift FL-17 detected")
else:
    print("\n✗ Forklift FL-17 not detected")

# 6. Search for the word injuries
if "injuries" in all_text.lower():
    print("\nThe word 'injuries' was found.")
else:
    print("\nThe word 'injuries' was not found.")

# Split into lines
lines = all_text.splitlines()

# 7. Extract lines mentioning inspection
print("\n=== LINES CONTAINING 'inspection' ===")
inspection_lines = []

for line in lines:
    if "inspection" in line.lower():
        inspection_lines.append(line)
        print(line)

# 8. Save the OCR output into ocr_result.txt
with open("ocr_result.txt", "w", encoding="utf-8") as file:
    file.write(all_text)

print("\n OCR output saved to ocr_result.txt")

# 9. Count the number of times inspection appears
inspection_count = all_text.lower().count("inspection")
print(f"\n'inspection' appears {inspection_count} times")

# 10. Print all lines containing Loading Bay
print("\n LINES CONTAINING 'Loading Bay'")

for line in lines:
    if "loading bay" in line.lower():
        print(line)