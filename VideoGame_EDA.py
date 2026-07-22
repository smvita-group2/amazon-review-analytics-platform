# Databricks notebook source
import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

pd.set_option("display.max_columns", None)
plt.style.use("default")

# COMMAND ----------

BASE_PATH = "/Volumes/project/proj_schema/proj_volume/Bronze/"

# COMMAND ----------

REVIEWS_PATH = f"{BASE_PATH}/Video_Games.parquet"

METADATA_PATH = f"{BASE_PATH}/meta_Video_Games.parquet"

# COMMAND ----------

# Reviews Dataset
reviews_df = spark.read.parquet(REVIEWS_PATH)

# Metadata Dataset
meta_df = spark.read.parquet(METADATA_PATH)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES REVIEWS DATASET SCHEMA")
print("=" * 80)

reviews_df.printSchema()

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES METADATA DATASET SCHEMA")
print("=" * 80)

meta_df.printSchema()

# COMMAND ----------

import pyarrow.parquet as pq

BASE_PATH = "/Volumes/project/proj_schema/proj_volume"

REVIEWS_PATH = f"{BASE_PATH}/Video_Games.parquet"
METADATA_PATH = f"{BASE_PATH}/meta_Video_Games.parquet"

# Load Reviews
reviews_df = spark.read.parquet(REVIEWS_PATH)

# Load Metadata with duplicate column handling
table = pq.read_table(METADATA_PATH)

cols = table.column_names

seen = {}
new_cols = []

for c in cols:
    if c in seen:
        seen[c] += 1
        new_cols.append(f"{c}_{seen[c]}")
    else:
        seen[c] = 0
        new_cols.append(c)

pdf = table.to_pandas()
pdf.columns = new_cols

meta_df = spark.createDataFrame(pdf)

print("Reviews Dataset Loaded Successfully")
print("Metadata Dataset Loaded Successfully")

# COMMAND ----------

meta_df = meta_df.drop("details")

# COMMAND ----------

from pyspark.sql import Row

shape_df = spark.createDataFrame([
    Row(
        Dataset="Reviews",
        Rows=reviews_df.count(),
        Columns=len(reviews_df.columns)
    ),
    Row(
        Dataset="Metadata",
        Rows=meta_df.count(),
        Columns=len(meta_df.columns)
    )
])

display(shape_df)

# COMMAND ----------

import pandas as pd

# Reviews Dataset Columns
reviews_columns = pd.DataFrame({
    "Video Games Reviews Columns": reviews_df.columns
})

# Metadata Dataset Columns
metadata_columns = pd.DataFrame({
    "Video Games Metadata Columns": meta_df.columns
})

display(reviews_columns)
display(metadata_columns)

# COMMAND ----------

import pandas as pd

def datatype_summary(df):
    return pd.DataFrame(
        [
            (field.name, field.dataType.simpleString())
            for field in df.schema.fields
        ],
        columns=["Column", "Data Type"]
    )

print("=" * 80)
print("VIDEO GAMES REVIEWS DATASET - DATA TYPES")
print("=" * 80)

display(datatype_summary(reviews_df))

print("=" * 80)
print("VIDEO GAMES METADATA DATASET - DATA TYPES")
print("=" * 80)

display(datatype_summary(meta_df))

# COMMAND ----------

import pandas as pd

REVIEWS_PATH = "/Volumes/project/proj_schema/proj_volume/Video_Games.parquet"
METADATA_PATH = "/Volumes/project/proj_schema/proj_volume/meta_Video_Games.parquet"

def folder_size(path):
    total_size = 0

    for file in dbutils.fs.ls(path):
        total_size += file.size

    return total_size / (1024 ** 3)   # Convert bytes to GB

reviews_size = folder_size(REVIEWS_PATH)
metadata_size = folder_size(METADATA_PATH)

memory_df = pd.DataFrame({
    "Dataset": ["Video Games Reviews", "Video Games Metadata"],
    "Storage Size (GB)": [
        f"{reviews_size:.2f}",
        f"{metadata_size:.2f}"
    ]
})

display(memory_df)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES REVIEWS DATASET")
print("=" * 80)

display(reviews_df.limit(10))

print("\n")

print("=" * 80)
print("VIDEO GAMES METADATA DATASET")
print("=" * 80)

display(meta_df.limit(10))

# COMMAND ----------

from pyspark.sql.functions import col

print("=" * 80)
print("LATEST VIDEO GAMES REVIEWS")
print("=" * 80)

display(
    reviews_df
        .orderBy(col("timestamp").desc())
        .limit(10)
)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES METADATA")
print("=" * 80)

display(
    meta_df.limit(10)
)

# COMMAND ----------

from pyspark.sql.functions import countDistinct
import pandas as pd

candidate_keys = pd.DataFrame({
    "Dataset": [
        "Video Games Reviews",
        "Video Games Reviews",
        "Video Games Metadata"
    ],
    "Candidate Key": [
        "asin",
        "parent_asin",
        "parent_asin"
    ],
    "Distinct Values": [
        reviews_df.select(countDistinct("asin")).collect()[0][0],
        reviews_df.select(countDistinct("parent_asin")).collect()[0][0],
        meta_df.select(countDistinct("parent_asin")).collect()[0][0]
    ]
})

display(candidate_keys)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES DATASET SUMMARY")
print("=" * 80)

total_reviews = reviews_df.count()
total_products = meta_df.count()

print(f"Total Reviews          : {total_reviews:,}")
print(f"Total Products (Meta)  : {total_products:,}")

# COMMAND ----------

# ==========================================
# Composite Key Validation - Video Games Reviews
# ==========================================

print("=" * 80)
print("VIDEO GAMES REVIEWS - COMPOSITE KEY VALIDATION")
print("=" * 80)

# Total number of reviews
total_reviews = reviews_df.count()

print(f"Total Reviews: {total_reviews:,}")

# Count unique composite keys
composite_count = (
    reviews_df
        .select(
            "parent_asin",
            "user_id",
            "timestamp"
        )
        .distinct()
        .count()
)

print(f"Unique Composite Keys: {composite_count:,}")

# Validate uniqueness
if composite_count == total_reviews:
    print("\n✅ Composite Key (parent_asin, user_id, timestamp) is UNIQUE.")
else:
    duplicate_records = total_reviews - composite_count
    print(f"\n❌ Composite Key contains {duplicate_records:,} duplicate record(s).")

# COMMAND ----------

from pyspark.sql.functions import count, col

print("=" * 80)
print("VIDEO GAMES REVIEWS - DUPLICATE COMPOSITE KEY CHECK")
print("=" * 80)

# Find duplicate composite keys
duplicates = (
    reviews_df
    .groupBy("parent_asin", "user_id", "timestamp")
    .agg(count("*").alias("duplicate_count"))
    .filter(col("duplicate_count") > 1)
)

# Count duplicate composite keys
duplicate_count = duplicates.count()

print(f"Duplicate Composite Keys: {duplicate_count:,}")

# Display duplicate records
display(
    duplicates.orderBy(col("duplicate_count").desc())
)

# COMMAND ----------

from pyspark.sql.functions import count, col

print("=" * 80)
print("VIDEO GAMES REVIEWS - EXACT DUPLICATE ROWS")
print("=" * 80)

# Find exact duplicate rows
exact_duplicates = (
    reviews_df
    .groupBy(reviews_df.columns)
    .agg(count("*").alias("duplicate_count"))
    .filter(col("duplicate_count") > 1)
)

# Count duplicate rows
duplicate_rows = exact_duplicates.count()

print(f"Exact Duplicate Rows: {duplicate_rows:,}")

# Display duplicate rows
display(
    exact_duplicates.orderBy(col("duplicate_count").desc())
)

# COMMAND ----------

from pyspark.sql.functions import countDistinct
import pandas as pd

# Count distinct products in Reviews dataset
reviews_products = (
    reviews_df
    .select(countDistinct("parent_asin").alias("Distinct Products"))
    .collect()[0][0]
)

# Count distinct products in Metadata dataset
metadata_products = (
    meta_df
    .select(countDistinct("parent_asin").alias("Distinct Products"))
    .collect()[0][0]
)

# Create summary table
relationship_df = pd.DataFrame({
    "Dataset": [
        "Video Games Reviews",
        "Video Games Metadata"
    ],
    "Distinct parent_asin": [
        reviews_products,
        metadata_products
    ]
})

display(relationship_df)

# COMMAND ----------

from pyspark.sql.functions import countDistinct

reviews_products = reviews_df.select(countDistinct("parent_asin")).first()[0]
metadata_products = meta_df.select(countDistinct("parent_asin")).first()[0]

display(
    spark.createDataFrame(
        [
            ("Video Games Reviews", reviews_products),
            ("Video Games Metadata", metadata_products)
        ],
        ["Dataset", "Distinct parent_asin"]
    )
)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES - PRODUCTS IN METADATA BUT NOT IN REVIEWS")
print("=" * 80)

missing_reviews = (
    meta_df
    .select("parent_asin")
    .distinct()
    .join(
        reviews_df.select("parent_asin").distinct(),
        on="parent_asin",
        how="left_anti"
    )
)

print(f"Products in Metadata but not in Reviews: {missing_reviews.count():,}")

display(missing_reviews)

# COMMAND ----------

print("=" * 80)
print("VIDEO GAMES - PRODUCTS IN METADATA BUT NOT IN REVIEWS")
print("=" * 80)

unused_metadata = (
    meta_df
    .select("parent_asin")
    .distinct()
    .join(
        reviews_df
            .select("parent_asin")
            .distinct(),
        on="parent_asin",
        how="left_anti"
    )
)

# Count products present only in Metadata
unused_count = unused_metadata.count()

print(f"Products in Metadata but not in Reviews: {unused_count:,}")

# Display the products
display(unused_metadata)

# COMMAND ----------

unused_metadata = (
    meta_df
    .select("parent_asin")
    .distinct()
    .join(
        reviews_df.select("parent_asin").distinct(),
        on="parent_asin",
        how="left_anti"
    )
)

print(f"Products in Metadata but not in Reviews: {unused_metadata.count():,}")

# COMMAND ----------

from pyspark.sql.functions import col

metadata_duplicates = (
    meta_df
    .groupBy("parent_asin")
    .count()
    .filter(col("count") > 1)
)

print(f"Duplicate parent_asin in Metadata: {metadata_duplicates.count():,}")


# COMMAND ----------

from pyspark.sql.functions import col

review_duplicates = (
    reviews_df
    .groupBy("parent_asin")
    .count()
    .filter(col("count") > 1)
)

print(f"Products with Multiple Reviews: {review_duplicates.count():,}")

# COMMAND ----------

import pandas as pd

key_summary = pd.DataFrame({
    "Dataset": [
        "Video Games Metadata",
        "Video Games Reviews"
    ],
    "Primary Key": [
        "parent_asin",
        "No Natural Primary Key"
    ],
    "Logical Identifier": [
        "-",
        "(parent_asin, user_id, timestamp)"
    ],
    "Foreign Key": [
        "-",
        "parent_asin"
    ]
})

display(key_summary)

# COMMAND ----------

from pyspark.sql.functions import countDistinct, min, max, count

print("=" * 80)
print("VIDEO GAMES REVIEWS DATASET SUMMARY")
print("=" * 80)

reviews_summary = (
    reviews_df
    .select(
        count("*").alias("Total Reviews"),
        countDistinct("parent_asin").alias("Distinct Products"),
        countDistinct("user_id").alias("Distinct Users"),
        min("timestamp").alias("Earliest Review"),
        max("timestamp").alias("Latest Review")
    )
)

display(reviews_summary)

# COMMAND ----------

from pyspark.sql.functions import count, countDistinct, min, max

print("=" * 80)
print("VIDEO GAMES METADATA DATASET SUMMARY")
print("=" * 80)

metadata_summary = (
    meta_df
    .select(
        count("*").alias("Total Products"),
        countDistinct("parent_asin").alias("Distinct Products"),
        countDistinct("main_category").alias("Main Categories"),
        countDistinct("store").alias("Stores"),
        min("average_rating").alias("Minimum Rating"),
        max("average_rating").alias("Maximum Rating")
    )
)

display(metadata_summary)

# COMMAND ----------

import pandas as pd

join_validation = pd.DataFrame({
    "Validation Check": [
        "Products in Reviews but not Metadata",
        "Products in Metadata but not Reviews"
    ],
    "Count": [
        missing_products.count(),
        unused_metadata.count()
    ]
})

display(join_validation)

# COMMAND ----------

matched_review_records = (
    reviews_df
    .join(
        meta_df.select("parent_asin").distinct(),
        on="parent_asin",
        how="inner"
    )
    .count()
)

matched_summary = spark.createDataFrame(
    [("Matched Review Records", matched_review_records)],
    ["Metric", "Count"]
)

display(matched_summary)

# COMMAND ----------

import pandas as pd

profile_summary = pd.DataFrame({
    "Dataset": [
        "Video Games Reviews",
        "Video Games Metadata"
    ],
    "Rows": [
        f"{reviews_df.count():,}",
        f"{meta_df.count():,}"
    ],
    "Columns": [
        len(reviews_df.columns),
        len(meta_df.columns)
    ]
})

display(profile_summary)

# COMMAND ----------

import pandas as pd
from pyspark.sql.types import *

# Function to count column types
def count_column_types(df):
    numeric = 0
    string = 0
    boolean = 0
    array = 0
    timestamp = 0

    for field in df.schema.fields:
        if isinstance(field.dataType, NumericType):
            numeric += 1
        elif isinstance(field.dataType, StringType):
            string += 1
        elif isinstance(field.dataType, BooleanType):
            boolean += 1
        elif isinstance(field.dataType, ArrayType):
            array += 1
        elif isinstance(field.dataType, TimestampType):
            timestamp += 1

    return numeric, string, boolean, array, timestamp


# Reviews Dataset
r_numeric, r_string, r_boolean, r_array, r_timestamp = count_column_types(reviews_df)

# Metadata Dataset
m_numeric, m_string, m_boolean, m_array, m_timestamp = count_column_types(meta_df)

# Summary Table
column_summary = pd.DataFrame({
    "Dataset": ["Video Games Reviews", "Video Games Metadata"],
    "Total Columns": [len(reviews_df.columns), len(meta_df.columns)],
    "Numeric Columns": [r_numeric, m_numeric],
    "String Columns": [r_string, m_string],
    "Boolean Columns": [r_boolean, m_boolean],
    "Array Columns": [r_array, m_array],
    "Timestamp Columns": [r_timestamp, m_timestamp]
})

display(column_summary)

# COMMAND ----------

from pyspark.sql.functions import countDistinct
import pandas as pd

reviews_cardinality = {
    "parent_asin": reviews_df.select(countDistinct("parent_asin")).first()[0],
    "user_id": reviews_df.select(countDistinct("user_id")).first()[0],
    "rating": reviews_df.select(countDistinct("rating")).first()[0],
    "verified_purchase": reviews_df.select(countDistinct("verified_purchase")).first()[0]
}

metadata_cardinality = {
    "parent_asin": meta_df.select(countDistinct("parent_asin")).first()[0],
    "main_category": meta_df.select(countDistinct("main_category")).first()[0],
    "store": meta_df.select(countDistinct("store")).first()[0]
}

cardinality_df = pd.DataFrame({
    "Dataset": [
        "Reviews",
        "Reviews",
        "Reviews",
        "Reviews",
        "Metadata",
        "Metadata",
        "Metadata"
    ],
    "Column": [
        "parent_asin",
        "user_id",
        "rating",
        "verified_purchase",
        "parent_asin",
        "main_category",
        "store"
    ],
    "Distinct Values": [
        reviews_cardinality["parent_asin"],
        reviews_cardinality["user_id"],
        reviews_cardinality["rating"],
        reviews_cardinality["verified_purchase"],
        metadata_cardinality["parent_asin"],
        metadata_cardinality["main_category"],
        metadata_cardinality["store"]
    ]
})

cardinality_df

# COMMAND ----------

from pyspark.sql.functions import col, when, sum, trim, size
from pyspark.sql.types import StringType, ArrayType, MapType
import pandas as pd

print("=" * 80)
print("VIDEO GAMES REVIEWS - MISSING VALUE ANALYSIS")
print("=" * 80)

expressions = []

for field in reviews_df.schema.fields:
    c = field.name
    dt = field.dataType

    # Check for missing values based on data type
    if isinstance(dt, StringType):
        condition = col(c).isNull() | (trim(col(c)) == "")

    elif isinstance(dt, (ArrayType, MapType)):
        condition = col(c).isNull() | (size(col(c)) == 0)

    else:
        condition = col(c).isNull()

    expressions.append(
        sum(
            when(condition, 1).otherwise(0)
        ).alias(c)
    )

# Calculate missing values
reviews_null_df = (
    reviews_df
    .select(expressions)
    .toPandas()
    .T
    .reset_index()
)

reviews_null_df.columns = ["Column", "Missing Values"]

# Calculate missing percentage
total_rows = reviews_df.count()

reviews_null_df["Missing %"] = (
    reviews_null_df["Missing Values"] / total_rows * 100
).round(2)

# Sort by highest missing percentage
reviews_null_df = reviews_null_df.sort_values(
    "Missing %",
    ascending=False
)

display(reviews_null_df)

# COMMAND ----------

from pyspark.sql.functions import col, when, sum, trim, size
from pyspark.sql.types import StringType, ArrayType, MapType
import pandas as pd

print("=" * 80)
print("VIDEO GAMES METADATA - MISSING VALUE ANALYSIS")
print("=" * 80)

expressions = []

for field in meta_df.schema.fields:
    c = field.name
    dt = field.dataType

    if isinstance(dt, StringType):
        condition = col(c).isNull() | (trim(col(c)) == "")

    elif isinstance(dt, (ArrayType, MapType)):
        condition = col(c).isNull() | (size(col(c)) == 0)

    else:
        condition = col(c).isNull()

    expressions.append(
        sum(
            when(condition, 1).otherwise(0)
        ).alias(c)
    )

# Calculate missing values
metadata_null_df = (
    meta_df
    .select(expressions)
    .toPandas()
    .T
    .reset_index()
)

metadata_null_df.columns = ["Column", "Missing Values"]

# Calculate missing percentage
total_rows = meta_df.count()

metadata_null_df["Missing %"] = (
    metadata_null_df["Missing Values"] / total_rows * 100
).round(2)

# Sort by highest missing percentage
metadata_null_df = metadata_null_df.sort_values(
    "Missing %",
    ascending=False
)

display(metadata_null_df)

# COMMAND ----------

duplicate_groups = (
    reviews_df
    .groupBy(reviews_df.columns)
    .count()
    .filter("count > 1")
)

duplicate_count = duplicate_groups.count()

duplicate_summary = pd.DataFrame({
    "Metric": ["Duplicate Records"],
    "Value": [f"{duplicate_count:,}"]
})

duplicate_summary

# COMMAND ----------

from pyspark.sql.functions import col
import pandas as pd

# Count invalid ratings (ratings should be between 1 and 5)
invalid_ratings = (
    reviews_df
    .filter(
        (col("rating") < 1) |
        (col("rating") > 5)
    )
    .count()
)

# Create summary table
quality_rating = pd.DataFrame({
    "Validation": ["Invalid Ratings"],
    "Count": [invalid_ratings]
})

# Display the result
display(quality_rating)

# COMMAND ----------

meta_df.select("price").printSchema()

# COMMAND ----------

meta_df.schema["price"].dataType

# COMMAND ----------

spark.conf.set("spark.sql.ansi.enabled", "true")

# COMMAND ----------

from pyspark.sql.functions import expr
import pandas as pd

print("=" * 80)
print("VIDEO GAMES METADATA - NEGATIVE PRICE VALIDATION")
print("=" * 80)

# Count products with negative prices
invalid_prices = (
    meta_df
    .filter(
        expr("try_cast(price AS DOUBLE) IS NOT NULL") &
        expr("try_cast(price AS DOUBLE) < 0")
    )
    .count()
)

# Create summary table
price_validation = pd.DataFrame({
    "Validation": ["Negative Prices"],
    "Count": [invalid_prices]
})

display(price_validation)

# COMMAND ----------

from pyspark.sql.functions import col, trim
import pandas as pd

print("=" * 80)
print("VIDEO GAMES REVIEWS - BLANK REVIEW TEXT VALIDATION")
print("=" * 80)

blank_reviews = (
    reviews_df
    .filter(
        col("text").isNull() |
        (trim(col("text")) == "")
    )
    .count()
)

blank_review_summary = pd.DataFrame({
    "Validation": ["Blank Review Text"],
    "Count": [blank_reviews]
})

display(blank_review_summary)

# COMMAND ----------

from pyspark.sql.functions import col, trim
import pandas as pd

invalid_categories = (
    meta_df
    .filter(
        col("main_category").isNull() |
        (trim(col("main_category")) == "")
    )
    .count()
)

category_validation = pd.DataFrame({
    "Validation": ["Missing/Blank Main Category"],
    "Count": [invalid_categories]
})

display(category_validation)

# COMMAND ----------

import pandas as pd

print("=" * 80)
print("VIDEO GAMES DATA QUALITY REPORT")
print("=" * 80)

data_quality_report = pd.DataFrame({
    "Quality Check": [
        "Invalid Ratings",
        "Negative Prices",
        "Blank Review Text",
        "Missing/Blank Main Category",
        "Invalid Timestamps"
    ],
    "Count": [
        invalid_ratings,
        invalid_prices,
        blank_reviews,
        invalid_categories,
        invalid_timestamps
    ],
    "Status": [
        "Passed" if invalid_ratings == 0 else "Review Required",
        "Passed" if invalid_prices == 0 else "Review Required",
        "Passed" if blank_reviews == 0 else "Minor Issue",
        "Passed" if invalid_categories == 0 else "Missing Values",
        "Passed" if invalid_timestamps == 0 else "Review Required"
    ]
})

display(data_quality_report)