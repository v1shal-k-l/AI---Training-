import fitz
pdf_path = "EY_Digital_PDF_Practice.pdf"
doc = fitz.open("EY_Digital_PDF_Practice.pdf")
print("Pages:", len(doc))
for page in doc:
    print(page.get_text())

count_of_pages  = 0
for page in doc:
    count_of_pages += 1

print(count_of_pages)


word = "maintenance"

found = False

count_of_word = 0

with fitz.open(pdf_path) as doc:
    for page_num, page in enumerate(doc,start = 1):
        text = page.get_text()
        if word.lower() in text.lower():
            print(f"Found '{word}' on page {page_num}")
            found = True
        if "V303".lower() in text.lower():
            count_of_word +=1
print(count_of_word)

with fitz.open(pdf_path) as doc:
    if len(doc) < 2:
        raise ValueError("The PDF has less than 2 pages.")
    # Page 2 is index 1
    page = doc[1]
    text = page.get_text()
output_file = "digital_pdf_text.txt"
# Save extracted text to file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Page 2 text extracted and saved to '{output_file}'.")
