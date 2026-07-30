from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

# ----------------------------------------
# Create Spark Session
# ----------------------------------------

spark = SparkSession.builder \
    .appName("Merge Amazon Categories") \
    .getOrCreate()

# ----------------------------------------
# S3 Paths
# ----------------------------------------

VIDEO_PATH = "s3://ml-data-aws-transformer-bert/gold/ml/Video_Games/"

MUSIC_PATH = "s3://ml-data-aws-transformer-bert/gold/ml/Musical_Instruments/"

APPLIANCE_PATH = "s3://ml-data-aws-transformer-bert/gold/ml/Appliances/"

OUTPUT_PATH = "s3://ml-data-aws-transformer-bert/ml/preprocessing/merged_data/"

# ----------------------------------------
# Read Datasets
# ----------------------------------------

video = spark.read.parquet(VIDEO_PATH)

music = spark.read.parquet(MUSIC_PATH)

appliance = spark.read.parquet(APPLIANCE_PATH)

# ----------------------------------------
# Add Category Column
# ----------------------------------------

video = video.withColumn("category", lit("Video_Games"))

music = music.withColumn("category", lit("Musical_Instruments"))

appliance = appliance.withColumn("category", lit("Appliances"))

# ----------------------------------------
# Merge
# ----------------------------------------

merged = video.unionByName(music)

merged = merged.unionByName(appliance)

# ----------------------------------------
# Basic Verification
# ----------------------------------------

print("=" * 60)

print("Video Games :", video.count())

print("Musical Instruments :", music.count())

print("Appliances :", appliance.count())

print("=" * 60)

print("Merged Count :", merged.count())

print("=" * 60)

merged.printSchema()

# ----------------------------------------
# Save
# ----------------------------------------

merged.write.mode("overwrite").parquet(OUTPUT_PATH)

print("Merged dataset saved successfully.")

spark.stop()
