output "service_role_arn" {
  value = aws_iam_role.emr_service_role.arn
}

output "service_role_name" {
  value = aws_iam_role.emr_service_role.name
}

output "ec2_role_name" {
  value = aws_iam_role.emr_ec2_role.name
}

output "instance_profile_name" {
  value = aws_iam_instance_profile.emr_instance_profile.name
}