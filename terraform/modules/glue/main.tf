# ==========================================================
# Caller Identity & Local Dynamic Definitions
# ==========================================================

data "aws_caller_identity" "current" {}

locals {
  database_name = var.create_database ? aws_glue_catalog_database.this[0].name : var.database_name
  workflow_name = var.create_workflow ? aws_glue_workflow.pipeline_workflow[0].name : var.workflow_name
  crawler_name  = var.create_crawler ? aws_glue_crawler.this[0].name : var.crawler_name
  lab_role_arn  = var.lab_role_arn != null && var.lab_role_arn != "" ? var.lab_role_arn : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
}

# ==========================================================
# Glue Catalog Database (Created or Reused)
# ==========================================================

resource "aws_glue_catalog_database" "this" {
  count = var.create_database ? 1 : 0
  name  = var.database_name
}

# ==========================================================
# Script Deployment to S3
# ==========================================================

resource "aws_s3_object" "bronze_to_silver_reviews_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py"
  source = "${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

resource "aws_s3_object" "bronze_to_silver_metadata_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py"
  source = "${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

resource "aws_s3_object" "silver_master_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/silver_master/silver_master_glue.py"
  source = "${path.module}/../../../gluejobs/silver_master/silver_master_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/silver_master/silver_master_glue.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

resource "aws_s3_object" "gold_visualization_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/gold/gold_visualization/gold_visualization_glue.py"
  source = "${path.module}/../../../gluejobs/gold/gold_visualization/gold_visualization_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/gold/gold_visualization/gold_visualization_glue.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

resource "aws_s3_object" "gold_aggregates_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/gold/gold_aggergates/gold_aggregates.py"
  source = "${path.module}/../../../gluejobs/gold/gold_aggergates/gold_aggregates.py"
  etag   = filemd5("${path.module}/../../../gluejobs/gold/gold_aggergates/gold_aggregates.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

resource "aws_s3_object" "gold_ml_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/gold/gold_ml/gold_ml_hybrid_cleaned.py"
  source = "${path.module}/../../../gluejobs/gold/gold_ml/gold_ml_hybrid_cleaned.py"
  etag   = filemd5("${path.module}/../../../gluejobs/gold/gold_ml/gold_ml_hybrid_cleaned.py")

  lifecycle {
    ignore_changes = [
      tags,
      tags_all
    ]
  }
}

# ==========================================================
# Glue PySpark Jobs
# ==========================================================

resource "aws_glue_job" "bronze_to_silver_reviews" {
  name              = "${var.project_name}-${var.environment}-bronze-to-silver-reviews"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.bronze_to_silver_reviews_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.bucket_name}/logs/spark/"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "bronze_to_silver_metadata" {
  name              = "${var.project_name}-${var.environment}-bronze-to-silver-metadata"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.bronze_to_silver_metadata_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "silver_master" {
  name              = "${var.project_name}-${var.environment}-silver-master"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.silver_master_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "gold_visualization" {
  name              = "${var.project_name}-${var.environment}-gold-visualization"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.gold_visualization_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "gold_aggregates" {
  name              = "${var.project_name}-${var.environment}-gold-aggregates"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.gold_aggregates_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "gold_ml" {
  name              = "${var.project_name}-${var.environment}-gold-ml"
  role_arn          = local.lab_role_arn
  glue_version      = var.glue_version
  worker_type       = var.worker_type
  number_of_workers = var.number_of_workers
  timeout           = var.timeout

  command {
    name            = "glueetl"
    script_location = "s3://${var.bucket_name}/${aws_s3_object.gold_ml_script.key}"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--datasets"                         = "Appliances,Video_Games,Musical_Instruments"
    "--s3_bucket"                        = var.bucket_name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ==========================================================
# Glue Automated Pipeline Workflow & Conditional Triggers
# ==========================================================

resource "aws_glue_workflow" "pipeline_workflow" {
  count       = var.create_workflow ? 1 : 0
  name        = var.workflow_name
  description = "Automated end-to-end Medallion Data Pipeline workflow"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Trigger 1: Start Stage 1 (Bronze to Silver Jobs)
resource "aws_glue_trigger" "start_stage_1" {
  name          = "${var.project_name}-${var.environment}-trigger-stage-1"
  type          = "ON_DEMAND"
  workflow_name = local.workflow_name

  actions {
    job_name = aws_glue_job.bronze_to_silver_reviews.name
  }

  actions {
    job_name = aws_glue_job.bronze_to_silver_metadata.name
  }
}

# Trigger 2: Start Stage 2 (Silver Master Job) upon Stage 1 Completion
resource "aws_glue_trigger" "stage_2_silver_master" {
  name          = "${var.project_name}-${var.environment}-trigger-stage-2"
  type          = "CONDITIONAL"
  workflow_name = local.workflow_name

  predicate {
    logical = "AND"

    conditions {
      job_name = aws_glue_job.bronze_to_silver_reviews.name
      state    = "SUCCEEDED"
    }

    conditions {
      job_name = aws_glue_job.bronze_to_silver_metadata.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.silver_master.name
  }
}

# Trigger 3: Start Stage 3 (Gold Jobs) upon Stage 2 Completion
resource "aws_glue_trigger" "stage_3_gold" {
  name          = "${var.project_name}-${var.environment}-trigger-stage-3"
  type          = "CONDITIONAL"
  workflow_name = local.workflow_name

  predicate {
    logical = "AND"

    conditions {
      job_name = aws_glue_job.silver_master.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.gold_visualization.name
  }

  actions {
    job_name = aws_glue_job.gold_aggregates.name
  }

  actions {
    job_name = aws_glue_job.gold_ml.name
  }
}

# Trigger 4: Start Crawler upon Gold Jobs Completion
resource "aws_glue_trigger" "stage_4_crawler" {
  name          = "${var.project_name}-${var.environment}-trigger-stage-4"
  type          = "CONDITIONAL"
  workflow_name = local.workflow_name

  predicate {
    logical = "AND"

    conditions {
      job_name = aws_glue_job.gold_visualization.name
      state    = "SUCCEEDED"
    }

    conditions {
      job_name = aws_glue_job.gold_aggregates.name
      state    = "SUCCEEDED"
    }

    conditions {
      job_name = aws_glue_job.gold_ml.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = local.crawler_name
  }
}

# ==========================================================
# Glue Catalog Crawler (Created or Reused)
# ==========================================================

# Synchronizes Parquet datasets from S3 Silver and Gold layers into the Glue Data Catalog Database (amazon_reviews_db)
resource "aws_glue_crawler" "this" {
  count         = var.create_crawler ? 1 : 0
  name          = var.crawler_name
  role          = local.lab_role_arn
  database_name = local.database_name

  # Target S3 paths where PySpark ETL jobs write output
  s3_target {
    path = "s3://${var.bucket_name}/silver/"
  }

  s3_target {
    path = "s3://${var.bucket_name}/gold/"
  }

  schedule = var.crawler_schedule

  # Automatically update schemas and log deletions
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

  # Explicit dependency on Glue catalog database
  depends_on = [aws_glue_catalog_database.this]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}