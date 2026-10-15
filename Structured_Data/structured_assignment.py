import pandas as pd
import numpy as np
df = pd.read_csv("library_loans.csv")
# print(df.head())
# print(df[["Member_Name" , "Book_Category" , "Fine"]])

#print(df["Member_Name"].loc[df["Fine"] > 50])

# df["Status"] = np.where(df["Fine"] == 0, "No Fine" , "Fine Due")
# print(df["Status"])

#print(np.average(df["Days_Borrowed"]))

# total_fine_collected = df.groupby("Book_Category")["Fine"].sum()
# print(total_fine_collected)