import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

data = {
    "Product": ["Laptop", "Mouse", "Keyboard", "Laptop", "Mouse"],
    "City": ["Hyderabad", "Mumbai", "Delhi", "Hyderabad", "Delhi"],
    "Quantity": [2, 5, 3, 1, 4],
    "Price": [60000, 800, 1500, 60000, 800]
}
df = pd.DataFrame(data)
df["Total_Price"] = df["Quantity"] * df["Price"]

sales = df.groupby("Product")["Total_Price"].sum()

sales.plot(kind = "bar")
plt.title("Sales by Product")
plt.xlabel("Product")
plt.ylabel("Total Price")
plt.show()

sns.scatterplot(data=df, x="Product", y="Total_Price")
plt.title("Sales by Product")
plt.show()
