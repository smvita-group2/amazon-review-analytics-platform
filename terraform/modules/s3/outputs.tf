output "bucket_name" {
  value = var.create_bucket ? aws_s3_bucket.this[0].bucket : data.aws_s3_bucket.existing[0].bucket
}

output "bucket_arn" {
  value = var.create_bucket ? aws_s3_bucket.this[0].arn : data.aws_s3_bucket.existing[0].arn
}