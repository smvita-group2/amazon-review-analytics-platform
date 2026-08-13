# 05 Datasets

## Amazon Dataset Overview

The platform processes product metadata and customer reviews sourced from Amazon product categories (e.g., Electronics, Home & Kitchen, All Beauty).

## Dataset Schemas

### Product Metadata Schema (`meta_*.json`)
- `parent_asin` (string, Primary Key): Unique identifier for product family.
- `title` (string): Product title.
- `main_category` (string): High-level category.
- `categories` (array<string>): Hierarchical taxonomy.
- `price` (double): Product list price.
- `average_rating` (double): Average product rating.
- `rating_number` (int): Total rating count.
- `features` (array<string>): Bulleted feature list.
- `description` (array<string>): Product detailed description.
- `store` (string): Brand or store name.

### Customer Review Schema (`reviews_*.json`)
- `rating` (double): Star rating (1.0 to 5.0).
- `title` (string): Review headline.
- `text` (string): Main review narrative.
- `images` (array<struct>): Attached customer images.
- `parent_asin` (string, Foreign Key): Product identifier link.
- `user_id` (string): Reviewer identifier.
- `timestamp` (long / timestamp): Review creation epoch milliseconds.
- `helpful_vote` (int): Count of helpful votes.
- `verified_purchase` (boolean): Verified buyer flag.

## Partitioning Strategy
- S3 datasets are partitioned by `category` and `year/month` for optimized query execution in Athena and PySpark.
