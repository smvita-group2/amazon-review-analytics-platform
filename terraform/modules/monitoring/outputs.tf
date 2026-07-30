output "log_group_name" {
  value = aws_cloudwatch_log_group.emr.name
}

output "alarm_name" {
  value = aws_cloudwatch_metric_alarm.emr_cpu.alarm_name
}