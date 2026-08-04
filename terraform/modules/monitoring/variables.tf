variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "log_group_name" {
  type    = string
  default = "/aws/glue/amazon-review-analytics"
}