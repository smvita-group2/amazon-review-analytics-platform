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

