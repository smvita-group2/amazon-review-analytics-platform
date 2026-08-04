variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project Name"
  type        = string
  default     = "amazon-review-analytics"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Project S3 Bucket"
  type        = string
  default     = "amazon-review-analytics-group-2"
}

variable "create_bucket" {
  description = "Create a new S3 bucket or use an existing one"
  type        = bool
  default     = false
}

variable "create_database" {
  description = "Create a new Glue Database or reuse an existing one"
  type        = bool
  default     = false
}

variable "create_workflow" {
  description = "Create a new Glue Workflow or reuse an existing one"
  type        = bool
  default     = false
}

variable "create_crawler" {
  description = "Create a new Glue Crawler or reuse an existing one"
  type        = bool
  default     = false
}

variable "create_log_group" {
  description = "Create a new CloudWatch Log Group or reuse an existing one"
  type        = bool
  default     = false
}

variable "artifact_bucket" {
  description = "S3 bucket containing deployment artifacts"
  type        = string
  default     = "amazon-review-analytics-group-2"
}

variable "artifact_prefix" {
  description = "Artifact folder"
  type        = string
  default     = "artifacts"
}