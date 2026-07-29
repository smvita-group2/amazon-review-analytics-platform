output "aws_region" {
  value = var.aws_region
}

output "bucket_name" {
  value = module.s3.bucket_name
}

output "emr_cluster_id" {
  value = module.emr.cluster_id
}

output "glue_database" {
  value = module.glue.database_name
}

output "glue_crawler" {
  value = module.glue.crawler_name
}

output "log_group" {
  value = module.monitoring.log_group_name
}