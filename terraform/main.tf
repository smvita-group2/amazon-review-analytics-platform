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

module "emr_iam" {
  source = "./modules/emr_iam"

  project_name = var.project_name
  environment  = var.environment
}

module "security_groups" {
  source = "./modules/security_groups"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = var.vpc_id
}

module "emr" {
  source = "./modules/emr"

  project_name = var.project_name
  environment  = var.environment

  subnet_id = var.subnet_id

  service_role     = module.emr_iam.service_role_arn
  instance_profile = module.emr_iam.instance_profile_name

  master_security_group  = module.security_groups.master_security_group_id
  core_security_group    = module.security_groups.core_security_group_id
  service_security_group = module.security_groups.service_security_group_id

  log_uri = "s3://${module.s3.bucket_name}/logs/"

  master_instance_type = var.master_instance_type
  core_instance_type   = var.core_instance_type
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

  emr_cluster_id = module.emr.cluster_id
}