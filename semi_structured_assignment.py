import json

with open('festival_events.json') as file:
    events = json.load(file)


# for event in events:
#     print(event)

# for event in events:
#     print(event["location"]["city"])

# import pandas as pd
# df = pd.json_normalize(events)
# print(df["name"].loc[df["visitors"] > 700])

# for event in events:
#     print(event.get("features" , "No features listed"))

