data "aws_caller_identity" "current" {}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

module "s3" {
  source = "./modules/s3"

  create_bucket = var.create_bucket
  bucket_name   = var.bucket_name
  project_name  = var.project_name
  environment   = var.environment
}

module "glue" {
  source = "./modules/glue"

  project_name    = var.project_name
  environment     = var.environment
  category        = var.category
  datasets        = var.datasets
  create_database = var.create_database
  create_workflow = var.create_workflow
  create_crawler  = var.create_crawler

  bucket_name  = module.s3.bucket_name
  lab_role_arn = var.lab_role_arn != null && var.lab_role_arn != "" ? var.lab_role_arn : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name     = var.project_name
  environment      = var.environment
  create_log_group = var.create_log_group
}