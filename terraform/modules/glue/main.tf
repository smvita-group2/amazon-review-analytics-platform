data "aws_iam_role" "glue_role" {
  name = "LabRole"
}

resource "aws_glue_catalog_database" "this" {
  name = var.database_name
}

resource "aws_glue_crawler" "this" {
  name          = var.crawler_name
  role          = data.aws_iam_role.glue_role.arn
  database_name = aws_glue_catalog_database.this.name

  s3_target {
    path = "s3://${var.bucket_name}/silver/"
  }

  schedule = var.crawler_schedule

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0

    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}