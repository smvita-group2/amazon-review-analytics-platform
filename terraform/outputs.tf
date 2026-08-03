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

output "glue_workflow" {
  description = "Automated Glue Pipeline Workflow Name"
  value       = module.glue.workflow_name
}

output "glue_jobs" {
  description = "Map of all Glue PySpark Job Names"
  value       = module.glue.job_names
}

output "log_group" {
  description = "CloudWatch Log Group"
  value       = module.monitoring.log_group_name
}

output "emr_cluster_id" {
  description = "EMR Cluster ID"
  value       = var.enable_emr ? module.emr[0].cluster_id : null
}

output "emr_cluster_name" {
  description = "EMR Cluster Name"
  value       = var.enable_emr ? module.emr[0].cluster_name : null
}