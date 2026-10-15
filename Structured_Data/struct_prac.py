import pandas as pd
import numpy as np
df = pd.read_csv("structured_data.csv")
print(df)
# print(df[["Shipment_ID", "Origin", "Destination","Cost"]])
# print(df["Shipment_ID"].loc[df["Mode"]=="Road"])
# print(df["Shipment_ID"].loc[df["Weight_Kg"] > 150])

df["Cost_Per_Km"] = df["Cost"] / df["Distance_Km"]
print(df["Cost_Per_Km"])

print(np.average(df["Cost"]))
print(np.max(df["Cost"]))
print(np.min(df["Cost"]))

print(df.groupby("Mode")["Cost"].sum())

print(df.groupby("Mode")["Weight_Kg"].mean())

print(df.sort_values(by = "Cost", ascending = False))

print(df.loc[df["Delivery_Days"] <=1])
print(df.loc[df["Cost"] < 5000])