aws_region = "us-east-1"

project_name = "amazon-review-analytics"
environment  = "dev"

# Existing S3 Bucket (Reuse existing bucket)
create_bucket = false
bucket_name   = "amazon-review-analytics-group-2"

# Deployment artifacts
artifact_bucket = "amazon-review-analytics-group-2"
artifact_prefix = "artifacts"

# Reuse existing resources
create_database  = false
create_workflow  = false
create_crawler   = false
create_log_group = false