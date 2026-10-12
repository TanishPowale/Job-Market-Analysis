
import os
import sys
import subprocess
from datasets import load_dataset

# Always run commands from the project root
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_DIR)

HDFS_COMMAND = r"C:\hadoop-3.3.6\bin\hdfs.cmd"
CSV_FILE = os.path.join("data", "jobs.csv")
HDFS_CSV_PATH = "/jobmarket/raw/jobs.csv"

print("Downloading latest Lynceus job dataset...")

ds = load_dataset("Lynceus/jobs", split="train")

os.makedirs("data", exist_ok=True)
ds.to_csv(CSV_FILE, index=False)

print("Dataset downloaded successfully.")

print("Uploading dataset to Hadoop HDFS...")

subprocess.run(
    [
        HDFS_COMMAND,
        "dfs",
        "-put",
        "-f",
        CSV_FILE,
        HDFS_CSV_PATH
    ],
    check=True
)

print("Dataset uploaded to HDFS successfully.")

print("Running PySpark processing...")

subprocess.run(
    [sys.executable, "spark/process_jobs.py"],
    check=True,
    cwd=PROJECT_DIR
)

print("Updating SQLite database...")

subprocess.run(
    [sys.executable, "spark/parquet_to_sqlite.py"],
    check=True,
    cwd=PROJECT_DIR
)

print("Dataset update completed successfully!")
