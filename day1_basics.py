import pandas as pd

data = {
    "Product": ["Laptop", "Mouse", "Keyboard", "Laptop", "Mouse"],
    "City": ["Hyderabad", "Mumbai", "Delhi", "Hyderabad", "Delhi"],
    "Quantity": [2, 5, 3, 1, 4],
    "Price": [60000, 800, 1500, 60000, 800]
}
df = pd.DataFrame(data)
#print(df)
#print(df.head())
#print("Shape of the DataFrame" , df.shape)
#print(type(df))
print(df.dtypes)

## Data Manipulation
print(df[df["City"] == "Delhi"])
## Data Transformation
df["Total_Price"] = df["Quantity"] * df["Price"]
## Data Selection
print(df.groupby("Product")["Total_Price"].sum())
print(df.sort_values(by = "Total_Price", ascending = False))

