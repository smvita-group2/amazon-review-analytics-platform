# 10 Terraform IaC

## Infrastructure Provisioning Architecture

Located in `terraform/`:

```text
terraform/
├── main.tf                  # Root module instantiating child modules
├── variables.tf             # Input variable definitions
├── outputs.tf               # Infrastructure export attributes
├── backend.tf               # Terraform remote state configuration
├── terraform.tfvars.example # Sample variable overrides
└── modules/
    ├── s3/                  # Data lake S3 bucket creation and policy configuration
    ├── glue/                # Glue database, jobs, crawlers, and IAM role management
    └── monitoring/          # CloudWatch log groups and monitoring alarms
```

## Key Infrastructure Resources

- **`modules/s3`**: Creates target S3 data lake bucket with folder structure.
- **`modules/glue`**:
  - `aws_glue_catalog_database`: Database container for Glue tables.
  - `aws_glue_job`: Distributed PySpark job declarations referencing S3 script paths.
  - `aws_glue_crawler`: Automated catalog crawler.
  - `aws_iam_role`: Glue execution role attachment.
- **`modules/monitoring`**: Configures CloudWatch log retention and job failure alerts.

## State & Environment Control
- Environment variable `var.environment` switches between `dev`, `staging`, and `prod`.
