output "master_security_group_id" {
  value = aws_security_group.emr_master.id
}

output "core_security_group_id" {
  value = aws_security_group.emr_core.id
}

output "service_security_group_id" {
  value = aws_security_group.emr_service.id
}