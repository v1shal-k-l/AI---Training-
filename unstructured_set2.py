
with open("airport_operations_report.txt") as f:
    data = f.read()

print(data)


lines = 0
words = 0
chars = 0

for line in data.splitlines():
    lines += 1
    words += len(line.split())
    chars += words
print("Total number of line", lines)
print("Total number of words", words)
print("Total number of characters", chars)


words = ["flight", "runway", "operations", "reported"]

# Initialize counts
count = [0]*len(words)

for line in data.splitlines():
    for word in line.split():
        if word in words:
            count[words.index(word)] += 1

for i in range(len(words)):
    print(words[i], ":", count[i])

for line in data.splitlines():
    if "runway" in line.split():
        print(line)

words  = ["delay" , "delayed" , "delays"]
for line in data.splitlines():
    for word in words:
        if word in line.split():
            print(line)

keywords = {"delay", "delayed", "delays"}
for line in data.splitlines():
    if keywords.intersection(line.split()):
        print(line)

lines = []

for line in data.splitlines():
    if "reported" in line.split():
        lines.append(line)

ans = " ".join(lines)
print(ans)

words = ["emergency", "inspection", "weather", "passengers", "maintenance"]

count = {}

for word in words:
    count[word] = 0

for line in data.splitlines():
    for word in line.split():
        if word in count:
            count[word] += 1

print(count)

max_len = 0
ans = []
for line in data.splitlines():
    if max_len < len(line):
        max_len = max(max_len, len(line))
        ans = [line]
    elif len(line) == max_len:
        ans.append(line)

print(ans)


with open("filtered_airport_report.txt", "w") as file:
    for item in ans:
        file.write(item + "\n")

print("List written to filtered_airport_report.txt")