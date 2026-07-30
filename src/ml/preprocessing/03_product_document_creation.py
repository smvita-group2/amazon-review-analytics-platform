from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    first,
    collect_list,
    concat_ws,
    slice,
    coalesce,
    lit,
    col
)

spark = SparkSession.builder \
    .appName("Product Document Creation") \
    .getOrCreate()

INPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/merged_data/"
OUTPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/product_documents/"

# Read merged dataset
df = spark.read.parquet(INPUT_PATH)

# Replace NULL text values
df = df.fillna({
    "product_title": "",
    "description_text": "",
    "features_text": "",
    "review_text": "",
    "review_title": ""
})

# Group by Product
product_df = df.groupBy("parent_asin").agg(

    first("category").alias("category"),

    first("product_title").alias("product_title"),

    first("description_text").alias("description_text"),

    first("features_text").alias("features_text"),

    slice(
        collect_list(
            concat_ws(" ", col("review_title"), col("review_text"))
        ),
        1,
        20
    ).alias("reviews")
)

# Build one document column
product_df = product_df.withColumn(

    "document",

    concat_ws(
        " ",
        "product_title",
        "description_text",
        "features_text",
        concat_ws(" ", "reviews")
    )
)

# Select final columns
product_df = product_df.select(
    "parent_asin",
    "category",
    "product_title",
    "document"
)

print("=" * 60)
print("Total Product Documents :", product_df.count())
print("=" * 60)

product_df.write.mode("overwrite").parquet(OUTPUT_PATH)

print("Product documents created successfully.")

spark.stop()
