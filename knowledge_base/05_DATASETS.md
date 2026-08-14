# 05 Datasets

## Purpose
Defines the core data schemas, field types, primary keys, and partitioning strategies for Amazon product metadata and customer reviews.

## Related Files
- [04 Data Pipeline](04_DATA_PIPELINE.md)
- [07 Glue Pipeline](07_GLUE_PIPELINE.md)
- [11 Configuration](11_CONFIGURATION.md)

## Key Concepts
- **Product Metadata**: Catalog specs including ASIN, title, category, price, and features.
- **Customer Reviews**: Individual rating events linked to products via `parent_asin`.
- **Hive Partitioning**: Partitioning S3 data lake tables by category and date for query acceleration.

## Content

### Product Metadata Schema (`meta_*.json`)
- `parent_asin` (string, Primary Key): Unique identifier for product family.
- `title` (string): Product title.
- `main_category` (string): High-level category classification.
- `categories` (array<string>): Hierarchical category taxonomy.
- `price` (double): Product list price.
- `average_rating` (double): Average product rating.
- `rating_number` (int): Total rating count.
- `features` (array<string>): Bulleted feature list.
- `description` (array<string>): Product detailed description.
- `store` (string): Brand or store name.

### Customer Review Schema (`reviews_*.json`)
- `rating` (double): Star rating boundary [1.0 to 5.0].
- `title` (string): Review headline.
- `text` (string): Main review narrative text.
- `images` (array<struct>): Attached customer image URLs.
- `parent_asin` (string, Foreign Key): Product identifier link.
- `user_id` (string): Unique reviewer identifier.
- `timestamp` (long / timestamp): Review creation epoch milliseconds.
- `helpful_vote` (int): Count of helpful votes.
- `verified_purchase` (boolean): Verified purchase indicator.

### Partitioning Strategy
- S3 datasets are partitioned by `category` and `year/month` for optimized PySpark read performance and serverless Athena query execution.

## Next Reading
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
