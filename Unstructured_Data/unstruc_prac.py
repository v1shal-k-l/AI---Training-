with open ('unstructured_data.txt', 'r') as f:
    data = f.read()

print(data)

lines = 0
words = 0

for line in data.splitlines():
    lines += 1
    words += len(line.split())

print("Total number of line", lines)
print("Total number of words", words)

found = False
for line in data.splitlines():
    if  "maintenance" in line.split():
            found = True

print(found)

count = 0 ;
for line in data.splitlines():
    if "conveyor" in line.split():
        count += 1

print(count)

for line in data.splitlines():
    if "team" in line.split():
        print(line)

for line in data.splitlines():
    if "incident" in line.split():
        print(line)

lowercase_data = data.lower()

with open("lowercase_report.txt", "w", encoding="utf-8") as f:
    f.write(lowercase_data)

with open ("lowercase_report.txt", "r") as f:
    data_lower = f.read()

print(data_lower)

words = ["maintenance", "injuries", " inspection", "replacement", "operations"]

word = data_lower.split()
for words in words:
    print(f"{words} : found")

