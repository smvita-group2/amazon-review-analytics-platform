variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "subnet_id" {
  description = "Subnet where EMR cluster will be launched"
  type        = string
}

variable "service_role" {
  description = "EMR Service Role"
  type        = string
}

variable "instance_profile" {
  description = "EMR EC2 Instance Profile"
  type        = string
}

variable "log_uri" {
  description = "S3 Log URI"
  type        = string
}

variable "release_label" {
  description = "EMR Release"
  type        = string
  default     = "emr-7.10.0"
}

variable "master_instance_type" {
  description = "Master Instance Type"
  type        = string
  default     = "m5.xlarge"
}

variable "master_instance_count" {
  description = "Master node count"
  type        = number
  default     = 1
}

variable "core_instance_type" {
  description = "Core Instance Type"
  type        = string
  default     = "m5.xlarge"
}

variable "core_instance_count" {
  description = "Core node count"
  type        = number
  default     = 2
}

variable "applications" {
  description = "Applications to install"
  type        = list(string)

  default = [
    "Spark",
    "Hive",
    "Livy"
  ]
}

variable "auto_termination_idle_timeout" {
  description = "Idle timeout in seconds"
  type        = number
  default     = 3600
}

variable "keep_job_flow_alive" {
  description = "Keep cluster alive"
  type        = bool
  default     = true
}