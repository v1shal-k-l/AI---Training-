import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
data = {
"Employee": ["Aisha", "Rahul", "Neha", "Omar", "Priya", "Karan"],
"Department": ["HR", "IT", "Finance", "IT", "HR", "Finance"],
"Training_Hours": [12, 18, 10, 22, 15, 8],
"Assessment_Score": [78, 88, 72, 91, 84, 69],
"Completed": ["Yes", "Yes", "No", "Yes", "Yes","Yes"]
}
df = pd.DataFrame(data)
print(df)

print(df.head(4))

print(df[["Employee","Assessment_Score"]])

print(df.loc[df["Department"] == "IT", "Employee"])

print(df.loc[df["Assessment_Score"] > 80 , "Employee"])

print(df.loc[df["Completed"] == "Yes" , "Employee"])

it_scores = df[(df["Assessment_Score"] > 80 ) & (df["Department"] == "IT")]

df["Passed"] = np.where(df["Assessment_Score"] >= 75, "Pass", "Fail")
print(df[df["Passed"] == "Pass"])

print(np.average(df["Assessment_Score"]))
print(np.max(df["Assessment_Score"]))
print(np.min(df["Assessment_Score"]))

print(df.sort_values(by ="Assessment_Score", ascending = False))

print(df.groupby("Department")["Assessment_Score"].mean())

print(df.groupby("Department")["Training_Hours"].sum())

print(df.groupby("Department")["Employee"].count())

print(df.groupby(df["Completed"] == "Yes")["Employee"].count())

avg_score_by_dep = df.groupby("Department")["Assessment_Score"].mean()
avg_score_by_dep.plot(kind = "bar")
plt.show()

total_training_hour = df.groupby("Department")["Training_Hours"].sum()
total_training_hour.plot(kind = "bar")
plt.show()

sns.scatterplot(data = df , x = "Department", y = "Assessment_Score")
plt.show()

print(np.std(df["Assessment_Score"]))