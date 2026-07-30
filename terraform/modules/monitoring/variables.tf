variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "emr_cluster_id" {
  type = string
}

variable "log_group_name" {
  type    = string
  default = "/aws/emr/cluster"
}