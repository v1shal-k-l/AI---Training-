import json
with open("semi_struct_prac.json") as json_file:
    data = json.load(json_file)

print(data)

for x in data:
    print(x["incident_id"])

for x in data:
    print(x["location"]["city"])

for x in data:
    if x["severity"] == "High" :
        print(x)

for x in data:
    if x["category"] == "Safety":
        print(x)

for x in data:
    print(x.get("actions" , "No actions needed"))


counts = {}

for x in data:
    sev = x.get("severity", "Unknown").upper()
    counts[sev] = counts.get(sev, 0) + 1

for severity, count in counts.items():
    print(f"severity is ",severity, f"{count}")

for x in data :
    x["status"] = "open"
json.dumps(data)
print(data)
import pandas as pd
df = pd.json_normalize(data)
print(data)
print(df[["incident_id" , "severity" , "category" , "location.city" , "location.site"]])