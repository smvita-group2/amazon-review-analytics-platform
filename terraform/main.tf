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
  create_database = var.create_database

  bucket_name  = module.s3.bucket_name
  lab_role_arn = "arn:aws:iam::478582114103:role/amazon-review-analytics-dev-glue-role"
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name     = var.project_name
  environment      = var.environment
  create_log_group = var.create_log_group
}