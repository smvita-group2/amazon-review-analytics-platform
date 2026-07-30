from pyspark.sql import SparkSession
from pyspark.sql.functions import col, length

# -------------------------------------------------------
# Spark Session
# -------------------------------------------------------

spark = SparkSession.builder \
    .appName("Document Truncation") \
    .getOrCreate()

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

INPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/clean_documents/"
OUTPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/final_documents/"

MAX_DOCUMENT_LENGTH = 4000

# -------------------------------------------------------
# Read Clean Documents
# -------------------------------------------------------

df = spark.read.parquet(INPUT_PATH)

print("=" * 60)
print("Initial Documents :", df.count())
print("=" * 60)

# -------------------------------------------------------
# Document Length Statistics Before Truncation
# -------------------------------------------------------

print("Maximum Length Before Truncation")

df.select(length("document").alias("doc_length")) \
    .agg({"doc_length": "max"}) \
    .show()

# -------------------------------------------------------
# Truncate Documents
# -------------------------------------------------------

df = df.withColumn(
    "document",
    col("document").substr(1, MAX_DOCUMENT_LENGTH)
)

# -------------------------------------------------------
# Document Length Statistics After Truncation
# -------------------------------------------------------

print("Maximum Length After Truncation")

df.select(length("document").alias("doc_length")) \
    .agg({"doc_length": "max"}) \
    .show()

# -------------------------------------------------------
# Save Final Documents
# -------------------------------------------------------

df.write \
    .mode("overwrite") \
    .parquet(OUTPUT_PATH)

print("=" * 60)
print("Final documents saved successfully.")
print("=" * 60)

spark.stop()