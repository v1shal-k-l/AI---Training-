# import pandas as pd
# df = pd.read_csv("data.csv")
#
# print(df)
#
# print(df.shape)
#
# print(df[["Station", "Minutes"]])
#
# import json
# with open("support_tickets.json") as json_file:
#     tickets = json.load(json_file)
# print(tickets)
#
# # for ticket in tickets:
# #     print(ticket["ticket_id"],ticket["issue"],ticket["customer"]["name"])
# # print(tickets[1])
# # print(tickets[1].get("priority","Not assigned any"))
# # print(tickets[1].get("tags","Not assigned"))
#
# df = pd.json_normalize(tickets)
# print(df)


with open("incident_notes.txt") as file:
    text = file.read()

words = text.split()
print(len(words))

if "vibration" in text.lower():
    print("Vibration is Present")

print(text.lower().count("vibration"))