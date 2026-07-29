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
}

variable "create_bucket" {
  description = "Create a new S3 bucket or use an existing one"
  type        = bool
  default     = true
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EMR"
  type        = string
}

variable "master_instance_type" {
  type    = string
  default = "m5.xlarge"
}

variable "core_instance_type" {
  type    = string
  default = "m5.xlarge"
}