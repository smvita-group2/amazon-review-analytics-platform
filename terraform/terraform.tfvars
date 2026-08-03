aws_region = "us-east-1"

project_name = "amazon-review-analytics"
environment  = "dev"

# Existing bucket
create_bucket = true
bucket_name   = "amazon-review-analytics-shreyash-471112764802"

# Deployment artifacts
artifact_bucket = "amazon-review-analytics-shreyash-471112764802"
artifact_prefix = "artifacts"

# Network
vpc_id    = "vpc-01e9a6c45d239e514"
subnet_id = "subnet-0050635527648b3ae"

# EMR
enable_emr            = false
master_instance_type  = "m4.xlarge"
master_instance_count = 1

core_instance_type  = "m4.xlarge"
core_instance_count = 1