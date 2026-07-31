import sys

from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

from pyspark.context import SparkContext

from pyspark.sql import functions as F


#initialize Glue job
# Get Job Arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Initialize Spark & Glue Context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Initialize Job
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


# ----------------------------------------
# Configure Logger
# ----------------------------------------

logger = glueContext.get_logger()

#confugration
# Bucket
BUCKET = "amazon-review-analytics-group-2"

# Input Path
INPUT_PATH = f"s3://{BUCKET}/silver/master"

# Output Path
OUTPUT_PATH = f"s3://{BUCKET}/gold/ml/nlpdata"

# Categories
DATASETS = [
    "Musical_Instruments",
    "Appliances",
    "Video_Games",
    "Sports_and_Outdoors"
]

#required Column
REQUIRED_COLUMNS = [

    # Review Information
    "parent_asin",
    "user_id",
    "review_rating",
    "verified_purchase",
    "review_date",
    "review_title",
    "review_text",

    # Product Information
    "product_title",
    "main_category",
    "store",
    "sub_category",
    "description_text",
    "features_text",
    "product_image_url"
]
# default values
DEFAULT_VALUES = {

    "review_title": "",
    "review_text": "",

    "product_title": "",
    "main_category": "Unknown",
    "store": "Unknown",
    "sub_category": "Unknown",

    "description_text": "",
    "features_text": "",

    "product_image_url": "https://dummyimage.com/300x300/e5e7eb/6b7280.png&text=No+Image"

}
# ----------------------------------------
# Validate Required Columns
# ----------------------------------------

def validate_required_columns(df):
    """
    Validates that all required columns exist in the DataFrame.
    Raises an exception if any required column is missing.
    """

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise Exception(
            f"Missing Required Columns: {missing_columns}"
        )

    logger.info("All required columns are present.")

# ----------------------------------------
# Fill Missing Values
# ----------------------------------------

def fill_missing_values(df):
    """
    Fills missing values using predefined default values.
    """

    logger.info("Filling missing values...")

    df = df.fillna(DEFAULT_VALUES)

    logger.info("Missing values filled successfully.")

    return df
# ----------------------------------------
# Remove Duplicate Records
# ----------------------------------------

def remove_duplicates(df):
    """
    Removes duplicate records from the DataFrame.
    """

    logger.info("Removing duplicate records...")

    df = df.dropDuplicates()

    logger.info("Duplicate records removed successfully.")

    return df
# ----------------------------------------
# Create Combined Text
# ----------------------------------------

def create_combined_text(df):
    """
    Combines product and review information into a single text column.
    """

    logger.info("Creating combined_text column...")

    df = df.withColumn(
        "combined_text",
        F.concat_ws(
            " ",
            F.coalesce(F.col("product_title"), F.lit("")),
            F.coalesce(F.col("description_text"), F.lit("")),
            F.coalesce(F.col("features_text"), F.lit("")),
            F.coalesce(F.col("review_title"), F.lit("")),
            F.coalesce(F.col("review_text"), F.lit(""))
        )
    )

    logger.info("combined_text column created successfully.")

    return df
# ----------------------------------------
# Clean Combined Text
# ----------------------------------------

def clean_text(df):
    """
    Cleans the combined_text column for transformer models.
    """

    logger.info("Cleaning combined_text...")

    # Convert to lowercase
    df = df.withColumn(
        "combined_text",
        F.lower(F.col("combined_text"))
    )

    # Remove HTML tags
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            "<[^>]+>",
            " "
        )
    )

    # Remove URLs
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            r"https?://\S+|www\.\S+",
            " "
        )
    )

    # Remove Email IDs
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            r"\S+@\S+",
            " "
        )
    )

    # Remove Emojis / Non-ASCII Characters
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            r"[^\x00-\x7F]",
            " "
        )
    )

    # Remove Special Characters
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            r"[^a-zA-Z0-9\s]",
            " "
        )
    )

    # Normalize Multiple Spaces
    df = df.withColumn(
        "combined_text",
        F.regexp_replace(
            "combined_text",
            r"\s+",
            " "
        )
    )

    # Trim Leading & Trailing Spaces
    df = df.withColumn(
        "combined_text",
        F.trim(F.col("combined_text"))
    )

    logger.info("combined_text cleaned successfully.")

    return df

# ----------------------------------------
# Remove Empty Combined Text
# ----------------------------------------

def remove_empty_combined_text(df):
    """
    Removes rows where combined_text is empty after cleaning.
    """

    logger.info("Removing empty combined_text records...")

    df = df.filter(
        F.col("combined_text").isNotNull() &
        (F.length(F.trim(F.col("combined_text"))) > 0)
    )

    logger.info("Empty combined_text records removed successfully.")

    return df

# ----------------------------------------
# Main Processing Loop
# ----------------------------------------

for dataset in DATASETS:

    logger.info("=" * 80)
    logger.info(f"Starting Dataset : {dataset}")
    logger.info("=" * 80)

    input_path = f"{INPUT_PATH}/{dataset}"
    output_path = f"{OUTPUT_PATH}/{dataset}"

    df = None

    try:

        # ----------------------------------------
        # Read Data
        # ----------------------------------------

        logger.info(f"Reading : {input_path}")

        df = spark.read.parquet(input_path)

        # Validate Required Columns
        validate_required_columns(df)

        # Select Required Columns
        df = df.select(*REQUIRED_COLUMNS)

        # Fill Missing Values
        df = fill_missing_values(df)

        # Remove Duplicate Records
        df = remove_duplicates(df)

        # Create Combined Text
        df = create_combined_text(df)

        # Clean Text
        df = clean_text(df)

        # Remove Empty Text
        df = remove_empty_combined_text(df)

        

        # Repartition
        df = df.repartition("parent_asin")

       

        # Write Dataset
        logger.info(f"Writing : {output_path}")

        (
            df.write
            .mode("overwrite")
            .option("compression", "snappy")
            .parquet(output_path)
        )

        logger.info(f"{dataset} completed successfully.")

    except Exception:

          logger.exception(f"Dataset Failed : {dataset}")

    