# ==========================================================
# Glue Catalog Database
# ==========================================================

resource "aws_glue_catalog_database" "this" {
  name = var.database_name
}

# ==========================================================
# Script Deployment to S3
# ==========================================================

resource "aws_s3_object" "bronze_to_silver_reviews_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py"
  source = "${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_reviews_glue.py")
}

resource "aws_s3_object" "bronze_to_silver_metadata_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py"
  source = "${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/bronze_to_silver/bronze_to_silver_metadata_glue.py")
}

resource "aws_s3_object" "silver_master_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/silver_master/silver_master_glue.py"
  source = "${path.module}/../../../gluejobs/silver_master/silver_master_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/silver_master/silver_master_glue.py")
}

resource "aws_s3_object" "gold_visualization_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/gold/gold_visualization/gold_visualization_glue.py"
  source = "${path.module}/../../../gluejobs/gold/gold_visualization/gold_visualization_glue.py"
  etag   = filemd5("${path.module}/../../../gluejobs/gold/gold_visualization/gold_visualization_glue.py")
}

resource "aws_s3_object" "gold_aggregates_script" {
  bucket = var.bucket_name
  key    = "scripts/gluejobs/gold/gold_aggergates/gold_aggregates.py"
  source = "${path.module}/../../../gluejobs/gold/gold_aggergates/gold_aggregates.py"
  etag   = filemd5("${path.module}/../../../gluejobs/gold/gold_aggergates/gold_aggregates.py")
}

# ==========================================================
# Glue PySpark Jobs
# ==========================================================

resource "aws_glue_job" "bronze_to_silver_reviews" {
  name              = "${var.project_name}-${var.environment}-bronze-to-silver-reviews"
  role_arn          = var.lab_role_arn
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
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "bronze_to_silver_metadata" {
  name              = "${var.project_name}-${var.environment}-bronze-to-silver-metadata"
  role_arn          = var.lab_role_arn
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
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "silver_master" {
  name              = "${var.project_name}-${var.environment}-silver-master"
  role_arn          = var.lab_role_arn
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
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "gold_visualization" {
  name              = "${var.project_name}-${var.environment}-gold-visualization"
  role_arn          = var.lab_role_arn
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
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_glue_job" "gold_aggregates" {
  name              = "${var.project_name}-${var.environment}-gold-aggregates"
  role_arn          = var.lab_role_arn
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
  name        = "${var.project_name}-${var.environment}-pipeline-workflow"
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
  workflow_name = aws_glue_workflow.pipeline_workflow.name

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
  workflow_name = aws_glue_workflow.pipeline_workflow.name

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
  workflow_name = aws_glue_workflow.pipeline_workflow.name

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
}

# Trigger 4: Start Crawler upon Gold Jobs Completion
resource "aws_glue_trigger" "stage_4_crawler" {
  name          = "${var.project_name}-${var.environment}-trigger-stage-4"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.pipeline_workflow.name

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
  }

  actions {
    crawler_name = aws_glue_crawler.this.name
  }
}

# ==========================================================
# Glue Catalog Crawler
# ==========================================================

resource "aws_glue_crawler" "this" {
  name          = var.crawler_name
  role          = var.lab_role_arn
  database_name = aws_glue_catalog_database.this.name

  s3_target {
    path = "s3://${var.bucket_name}/silver/"
  }

  s3_target {
    path = "s3://${var.bucket_name}/gold/"
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