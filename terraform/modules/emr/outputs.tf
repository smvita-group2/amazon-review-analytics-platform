output "cluster_id" {
  value = aws_emr_cluster.this.id
}

output "cluster_name" {
  value = aws_emr_cluster.this.name
}

output "cluster_arn" {
  value = aws_emr_cluster.this.arn
}

output "master_public_dns" {
  value = aws_emr_cluster.this.master_public_dns
}