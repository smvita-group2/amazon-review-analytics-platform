aws_region = "us-east-1"

project_name = "amazon-review-analytics"
environment  = "dev"

# Existing bucket
create_bucket = false
bucket_name   = "amazon-review-analytics-group-2"

# Deployment artifacts
artifact_bucket = "amazon-review-analytics-group-2"
artifact_prefix = "artifacts"

# Network
vpc_id    = "vpc-023ac2f6325567736"
subnet_id = "subnet-00e3d0807c2aa3752"

# EMR
master_instance_type  = "m4.xlarge"
master_instance_count = 1

core_instance_type    = "m4.xlarge"
core_instance_count   = 1