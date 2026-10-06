with open("wildlife_report.txt") as file:
      report = file.read()

# print(report)

# words = report.split()
# count = len(words)
# print(count)

# if "elephant" in report:
#     print("True")
# else:
#     print("False")

# count_ele = 0
# for word in report.split():
#     if word == "elephant":
#         count_ele = count_ele + 1
#
# print(count_ele)

# with open("wildlife_report.txt") as file:
#     for line in file:
#         if "trail" in line:
#             print(line)

with open("wildlife_report.txt") as file:
    for line in file:
        for word in line.split():
            if word == "animal" in line:
                print(line)


