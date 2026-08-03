variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "database_name" {
  description = "Glue Catalog Database"
  type        = string
  default     = "amazon_reviews_db"
}

variable "crawler_name" {
  description = "Glue crawler name"
  type        = string
  default     = "amazon-review-crawler"
}

variable "crawler_schedule" {
  description = "Glue crawler schedule"
  type        = string
  default     = "cron(0 2 * * ? *)"
}

variable "lab_role_arn" {
  description = "Pre-built IAM LabRole ARN for federated accounts"
  type        = string
  default     = "arn:aws:iam::478582114103:role/amazon-review-analytics-dev-glue-role"
}

variable "glue_version" {
  description = "AWS Glue Version"
  type        = string
  default     = "4.0"
}

variable "worker_type" {
  description = "Glue Worker Type"
  type        = string
  default     = "G.1X"
}

variable "number_of_workers" {
  description = "Number of Glue Workers"
  type        = number
  default     = 2
}

variable "timeout" {
  description = "Glue job timeout in minutes"
  type        = number
  default     = 60
}