variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "create_log_group" {
  description = "Create a new CloudWatch Log Group or reuse an existing one"
  type        = bool
  default     = false
}

variable "log_group_name" {
  type    = string
  default = "/aws/glue/amazon-review-analytics"
}