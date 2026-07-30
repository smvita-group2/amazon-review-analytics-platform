output "aws_region" {
  description = "AWS Region"
  value       = var.aws_region
}

output "bucket_name" {
  description = "S3 Bucket"
  value       = module.s3.bucket_name
}

output "glue_database" {
  description = "Glue Database"
  value       = module.glue.database_name
}

output "glue_crawler" {
  description = "Glue Crawler"
  value       = module.glue.crawler_name
}

output "log_group" {
  description = "CloudWatch Log Group"
  value       = module.monitoring.log_group_name
}

output "emr_cluster_id" {
  description = "EMR Cluster ID"
  value       = module.emr.cluster_id
}

output "emr_cluster_name" {
  description = "EMR Cluster Name"
  value       = module.emr.cluster_name
}