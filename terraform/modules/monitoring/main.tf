resource "aws_cloudwatch_log_group" "app" {
  count             = var.create_log_group ? 1 : 0
  name              = "${var.log_group_name}/${var.project_name}-${var.environment}"
  retention_in_days = 30

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

locals {
  log_group_name = var.create_log_group ? aws_cloudwatch_log_group.app[0].name : "${var.log_group_name}/${var.project_name}-${var.environment}"
}