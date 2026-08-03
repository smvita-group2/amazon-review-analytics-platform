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
  default     = "arn:aws:iam::471112764802:role/LabRole"
}