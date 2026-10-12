
import sqlite3
from pyspark.sql import SparkSession

HDFS_PARQUET_PATH = "hdfs://localhost:9000/jobmarket/processed/jobs"
DB_FILE = "data/jobmarket.db"

spark = SparkSession.builder \
    .appName("JobMarketParquetToSQLite") \
    .master("local[*]") \
    .getOrCreate()

# Read cleaned Parquet data from HDFS
df = spark.read.parquet(HDFS_PARQUET_PATH)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    title TEXT,
    company TEXT,
    location TEXT,
    remote TEXT,
    posted TEXT
)
""")

# Prevent duplicate rows when the script is rerun
cursor.execute("DELETE FROM jobs")

# Insert the processed records into SQLite
rows = df.select(
    "title", "company", "location", "remote", "posted"
).toLocalIterator()

cursor.executemany(
    "INSERT INTO jobs VALUES (?, ?, ?, ?, ?)",
    (
        (
            row["title"],
            row["company"],
            row["location"],
            str(row["remote"]),
            row["posted"]
        )
        for row in rows
    )
)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM jobs")
count = cursor.fetchone()[0]

conn.close()
spark.stop()

print("SQLite database updated successfully!")
print("Total rows:", count)
