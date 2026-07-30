output "database_name" {
  value = aws_glue_catalog_database.this.name
}

output "crawler_name" {
  value = aws_glue_crawler.this.name
}

output "crawler_role_arn" {
  value = "arn:aws:iam::471112764802:role/LabRole"
}