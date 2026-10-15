import pandas as pd
df = pd.read_csv('renewable_energy.csv')
print(df)
mask = (df["Energy_Type"] == "Solar") | (df["Energy_Type"] == "Wind")
print(df["Plant_Name"].loc[mask])

df["Efficency_Percent"] = (df["Actual_Output_MW"] / df["Capacity_MW"])*100
print(df["Efficency_Percent"])

print(df["Plant_Name"].loc[df["Efficency_Percent"] > 85])
print(df.groupby("Energy_Type")["Efficency_Percent"].mean())
print(df.groupby("Energy_Type")["Maintenance_Cost"].sum())
print(df["Plant_Name"].loc[df["Maintenance_Cost"].idxmax()])

df["Cost_Per_MW"] = df["Maintenance_Cost"] / df["Actual_Output_MW"]
print(df["Cost_Per_MW"])

print(df.sort_values(by = "Cost_Per_MW", ascending = True))
mask = (df["Efficency_Percent"] > 85) | (df["Maintenance_Cost"] < 7000)

print(df["Plant_Name"].loc[mask])

from matplotlib import pyplot as plt
import seaborn as sns
sns.barplot(df, x = "Plant_Name", y = "Efficency_Percent")
plt.show()