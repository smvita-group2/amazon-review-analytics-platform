resource "aws_cloudwatch_log_group" "emr" {

  name = "${var.log_group_name}/${var.project_name}-${var.environment}"

  retention_in_days = 30

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_metric_alarm" "emr_cpu" {

  alarm_name = "${var.project_name}-${var.environment}-emr-high-cpu"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2

  metric_name = "IsIdle"

  namespace = "AWS/ElasticMapReduce"

  period = 300

  statistic = "Average"

  threshold = 0

  dimensions = {
    JobFlowId = var.emr_cluster_id
  }

  alarm_description = "EMR cluster idle state"

  treat_missing_data = "notBreaching"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}