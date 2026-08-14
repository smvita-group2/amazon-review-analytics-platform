# Task Prompt: AWS Cloud Infrastructure & Glue Operations

## Context Files to Load
Before beginning work on AWS Glue jobs, Crawlers, Workflows, S3 prefix structure, or Athena queries, you MUST load the following knowledge files:
1. `knowledge_base/01_ARCHITECTURE.md`
2. `knowledge_base/06_AWS_INFRASTRUCTURE.md`
3. `knowledge_base/07_GLUE_PIPELINE.md`
4. `knowledge_base/10_TERRAFORM.md`

## Instructions
- Ensure Glue jobs target AWS Glue 4.0 runtime standards.
- Store production script entrypoints under `s3://<bucket>/scripts/`.
- Ensure Glue Catalog databases use the naming convention `amazon_reviews_db_<environment>`.
- Use CloudWatch log groups under `/aws/glue/jobs/<project_name>` for tracking.
