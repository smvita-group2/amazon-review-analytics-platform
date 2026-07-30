resource "aws_s3_bucket" "this" {
  count  = var.create_bucket ? 1 : 0
  bucket = var.bucket_name

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "this" {
  count  = var.create_bucket ? 1 : 0
  bucket = aws_s3_bucket.this[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

locals {
  folders = [
    "bronze/",
    "silver/",
    "gold/",
    "scripts/",
    "logs/",
    "temp/"
  ]
}

resource "aws_s3_object" "folders" {
  for_each = var.create_bucket ? toset(local.folders) : toset([])

  bucket  = aws_s3_bucket.this[0].id
  key     = each.value
  content = ""
}