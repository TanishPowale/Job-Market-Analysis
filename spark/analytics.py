import sqlite3
import pandas as pd

conn = sqlite3.connect("data/jobmarket.db")

df = pd.read_sql_query("SELECT * FROM jobs", conn)

print("Total Jobs:", len(df))
print("\nTop 10 Job Roles:")
print(df["title"].value_counts().head(10))

print("\nTop 10 Companies:")
print(df["company"].value_counts().head(10))

print("\nTop 10 Locations:")
print(df["location"].value_counts().head(10))

print("\nRemote vs Onsite:")
print(df["remote"].value_counts())

conn.close()