from pypdf import PdfReader

# 1. Open the PDF
reader = PdfReader("EY_Digital_PDF_Practice.pdf")

# 2. Print the number of pages
print("Number of pages:", len(reader.pages))

# 3. Extract text from the first page
page1_text = reader.pages[0].extract_text()
print("\n--- First Page ---")
print(page1_text)

# 4. Extract text from the second page
page2_text = reader.pages[1].extract_text()
print("\n--- Second Page ---")
print(page2_text)

# 5. Combine text from both pages into one string
combined_text = page1_text + "\n" + page2_text

# 6. Check whether 'NorthStar Maintenance' exists in the PDF
if "NorthStar Maintenance" in combined_text:
    print("\nNorthStar Maintenance found.")
else:
    print("\nNorthStar Maintenance not found.")

# 7. Find the number of occurrences of the word 'vendor'
vendor_count = combined_text.lower().count("vendor")
print("Occurrences of 'vendor':", vendor_count)

# 8. Save the extracted content into pypdf_output.txt
with open("pypdf_output.txt", "w", encoding="utf-8") as file:
    file.write(combined_text)

print("Content saved to pypdf_output.txt")