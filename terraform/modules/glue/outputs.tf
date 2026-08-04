output "database_name" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.this.name
}

output "crawler_name" {
  description = "Glue catalog crawler name"
  value       = aws_glue_crawler.this.name
}

output "workflow_name" {
  description = "Automated pipeline workflow name"
  value       = aws_glue_workflow.pipeline_workflow.name
}

output "job_names" {
  description = "Map of all Glue PySpark job names"
  value = {
    bronze_to_silver_reviews  = aws_glue_job.bronze_to_silver_reviews.name
    bronze_to_silver_metadata = aws_glue_job.bronze_to_silver_metadata.name
    silver_master             = aws_glue_job.silver_master.name
    gold_visualization        = aws_glue_job.gold_visualization.name
    gold_aggregates           = aws_glue_job.gold_aggregates.name
    gold_ml                   = aws_glue_job.gold_ml.name
  }
}