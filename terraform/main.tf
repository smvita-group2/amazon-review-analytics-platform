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

########################################
# Identity
########################################

module "emr" {
  count  = var.enable_emr ? 1 : 0
  source = "./modules/emr"

  project_name = var.project_name
  environment  = var.environment

  subnet_id = var.subnet_id

  service_role     = "amazon-review-analytics-dev-emr-service-role"
  instance_profile = "amazon-review-analytics-dev-instance-profile"

  log_uri = "s3://${module.s3.bucket_name}/logs/"

  master_instance_type  = var.master_instance_type
  master_instance_count = var.master_instance_count

  core_instance_type  = var.core_instance_type
  core_instance_count = var.core_instance_count
}

module "glue" {

  source = "./modules/glue"

  project_name = var.project_name
  environment  = var.environment

  bucket_name = module.s3.bucket_name
}

module "monitoring" {

  source = "./modules/monitoring"

  project_name = var.project_name
  environment  = var.environment

  emr_cluster_id = var.enable_emr ? module.emr[0].cluster_id : "serverless-glue"
}