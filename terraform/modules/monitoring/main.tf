resource "aws_cloudwatch_log_group" "app" {
  name              = "${var.log_group_name}/${var.project_name}-${var.environment}"
  retention_in_days = 30

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}