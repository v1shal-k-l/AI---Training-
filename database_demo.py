import sqlite3
connection = sqlite3.connect("cinema.db")

cursor = connection.cursor()
# cursor.execute("""Create table if not exists bookings(
#     booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     movie TEXT,
#     seats INTEGER,
#     amount REAL
# )""")

# cursor.execute("""
# INSERT INTO bookings (movie, seats, amount)
# VALUES ('Solar Drift', 2, 700)
# """)
#
# cursor.execute("""
# INSERT INTO bookings (movie, seats, amount)
# VALUES ('Midnight Code', 4, 1200)
# """)
#
# connection.commit()
#
# cursor.execute("Select * from bookings")
# print(cursor.fetchall())
import pandas as pd
df = pd.read_sql_query("SELECT * FROM bookings", connection)
print(df.head())