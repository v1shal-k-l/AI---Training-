import json
with open("smart_home_devices.json", "r") as file:
    df = json.load(file)

print(df)

for x in df:
    print(x["device_id"],x["device_type"],x["room"])

for x in df:
    if x["status"] == "Active" :
        print(x)

for x in df:
    if x["metrics"]["battery"] < 60 :
        print(x)
for x in df:
    if "temperature" in x["metrics"] :
        print(x)

for x in df:
    if "alert" in x["metrics"] :
        print(x)

import pandas as pd
import numpy as np
data = pd.json_normalize(df)
print(data.groupby("device_type")["device_id"].count())

conditions = [
    data['metrics.battery'] >= 70,
    data['metrics.battery'] >= 50,   # Moderate battery
    True                   # Catch-all for < 50
]

choices = [
    'Good battery',
    'Moderate battery',
    'Low battery'
]

# Apply the rules
data['health_rule'] = np.select(conditions, choices, default='Low battery')

print(data)
print(type(data))

data.to_json(
    "updated_devices.json",
    orient="records",
    indent=4
)

mask = (data["status"] == "Active") & (data["metrics.battery"] < 70)
print(data.loc[mask])