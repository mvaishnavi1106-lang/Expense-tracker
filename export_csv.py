import sqlite3
import pandas as pd
import os

# Connect to your expenses.db
conn = sqlite3.connect("expenses.db")

# Read all data from your main table
df = pd.read_sql_query("SELECT * FROM expenses", conn)

# Export to CSV in same folder
csv_path = os.path.join(os.getcwd(), "expenses.csv")
df.to_csv(csv_path, index=False)

print("✅ CSV downloaded successfully at:", csv_path)

conn.close()
