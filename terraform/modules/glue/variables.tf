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

variable "category" {
  description = "Category filter (e.g. Appliances). If empty, processes all datasets."
  type        = string
  default     = "Appliances"
}

variable "datasets" {
  description = "Comma-separated list of default datasets"
  type        = string
  default     = "Appliances,Video_Games,Musical_Instruments"
}

variable "create_database" {
  description = "Create a new Glue Database or reuse an existing one"
  type        = bool
  default     = false
}

variable "database_name" {
  description = "Glue Catalog Database"
  type        = string
  default     = "amazon_reviews_db"
}

variable "create_workflow" {
  description = "Create a new Glue Workflow or reuse an existing one"
  type        = bool
  default     = false
}

variable "workflow_name" {
  description = "Glue Workflow Name"
  type        = string
  default     = "amazon-review-analytics-dev-pipeline-workflow"
}

variable "create_crawler" {
  description = "Create a new Glue Crawler or reuse an existing one"
  type        = bool
  default     = false
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
  description = "IAM Role ARN for AWS Glue jobs and crawler execution"
  type        = string
  default     = null
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