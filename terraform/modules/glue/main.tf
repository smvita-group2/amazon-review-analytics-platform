resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-${var.environment}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "glue.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy_attachment" "glue_s3" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_glue_catalog_database" "this" {
  name = var.database_name
}

resource "aws_glue_crawler" "this" {

  name          = var.crawler_name
  role          = aws_iam_role.glue_role.arn
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