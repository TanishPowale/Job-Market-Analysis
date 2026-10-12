
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim

spark = SparkSession.builder \
    .appName("JobMarketBDA") \
    .master("local[*]") \
    .getOrCreate()

# Read the raw dataset directly from Hadoop HDFS
df = spark.read.csv(
    "hdfs://localhost:9000/jobmarket/raw/jobs.csv",
    header=True,
    inferSchema=True
)

# Clean the dataset
df = df.dropDuplicates()

df = df.withColumn("title", trim(col("title")))
df = df.withColumn("company", trim(col("company")))
df = df.withColumn("location", trim(col("location")))

df = df.withColumn(
    "remote",
    lower(trim(col("remote").cast("string")))
)

df = df.withColumn(
    "remote",
    col("remote").isin("true")
)

df = df.filter(
    col("title").isNotNull() &
    col("company").isNotNull() &
    col("location").isNotNull()
)

df.createOrReplaceTempView("jobs")

print("Total cleaned jobs:", df.count())

print("\nTop 10 job roles:")
spark.sql("""
    SELECT title, COUNT(*) AS job_count
    FROM jobs
    GROUP BY title
    ORDER BY job_count DESC
    LIMIT 10
""").show(truncate=False)

print("\nTop 10 companies:")
spark.sql("""
    SELECT company, COUNT(*) AS job_count
    FROM jobs
    GROUP BY company
    ORDER BY job_count DESC
    LIMIT 10
""").show(truncate=False)

print("\nRemote vs Onsite:")
spark.sql("""
    SELECT remote, COUNT(*) AS job_count
    FROM jobs
    GROUP BY remote
    ORDER BY job_count DESC
""").show()

# Save cleaned data as Parquet in HDFS
df.write.mode("overwrite").parquet(
    "hdfs://localhost:9000/jobmarket/processed/jobs"
)

print("\nCleaned dataset saved to HDFS Parquet.")

spark.stop()
