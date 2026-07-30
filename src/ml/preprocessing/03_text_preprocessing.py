from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    trim,
    regexp_replace,
    lower,
    length
)

# -------------------------------------------------------
# Create Spark Session
# -------------------------------------------------------

spark = SparkSession.builder \
    .appName("Text Preprocessing") \
    .getOrCreate()

# -------------------------------------------------------
# S3 Paths
# -------------------------------------------------------

INPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/product_documents/"
OUTPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/clean_documents/"

# -------------------------------------------------------
# Read Product Documents
# -------------------------------------------------------

df = spark.read.parquet(INPUT_PATH)

print("=" * 60)
print("Initial Record Count :", df.count())
print("=" * 60)

# -------------------------------------------------------
# Remove NULL Documents
# -------------------------------------------------------

df = df.filter(col("document").isNotNull())

# -------------------------------------------------------
# Remove Empty Documents
# -------------------------------------------------------

df = df.filter(length(trim(col("document"))) > 0)

# -------------------------------------------------------
# Normalize Multiple Spaces
# -------------------------------------------------------

df = df.withColumn(
    "document",
    regexp_replace(col("document"), r"\s+", " ")
)

# -------------------------------------------------------
# Remove Leading & Trailing Spaces
# -------------------------------------------------------

df = df.withColumn(
    "document",
    trim(col("document"))
)

# -------------------------------------------------------
# Convert to Lowercase (Optional)
# -------------------------------------------------------

df = df.withColumn(
    "document",
    lower(col("document"))
)

# -------------------------------------------------------
# Remove Duplicate Products
# -------------------------------------------------------

df = df.dropDuplicates(["parent_asin"])

# -------------------------------------------------------
# Final Statistics
# -------------------------------------------------------

print("=" * 60)
print("Final Record Count :", df.count())
print("=" * 60)

# -------------------------------------------------------
# Save Clean Documents
# -------------------------------------------------------

df.write \
    .mode("overwrite") \
    .parquet(OUTPUT_PATH)

print("Clean documents saved successfully.")

spark.stop()