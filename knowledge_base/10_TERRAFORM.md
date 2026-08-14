# 10 Terraform IaC

## Purpose
Documents the Infrastructure as Code (IaC) modular configurations located in `terraform/`, detailing AWS resource creation for S3 storage, Glue catalog/jobs, IAM roles, and CloudWatch.

## Related Files
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md)
- [07 Glue Pipeline](07_GLUE_PIPELINE.md)
- [Terraform Modules Diagram](diagrams/terraform_modules.md)

## Key Concepts
- **Modular Terraform Architecture**: Declarative infrastructure split into reusable `s3`, `glue`, and `monitoring` modules.
- **Environment Isolation**: Managing dev/staging/prod workspaces via `var.environment` variable inputs.
- **Remote State Control**: S3 backend configuration for state storage (`backend.tf`).

## Content

### Infrastructure Directory Layout
```text
terraform/
├── main.tf                  # Root module instantiating child modules
├── variables.tf             # Input variable declarations
├── outputs.tf               # Infrastructure export attributes
├── backend.tf               # Terraform remote state configuration
├── terraform.tfvars.example # Sample environment variable overrides
└── modules/
    ├── s3/                  # S3 data lake bucket creation & lifecycle policies
    ├── glue/                # Glue database, PySpark jobs, crawlers, workflows & IAM
    └── monitoring/          # CloudWatch log groups & failure alarm triggers
```

### Module Resource Summary
- **`modules/s3`**: Creates target S3 data lake bucket and prefix folder structure (`/data/`, `/scripts/`, `/extra_jars/`).
- **`modules/glue`**:
  - `aws_glue_catalog_database`: Catalog database container.
  - `aws_glue_job`: Declarations for 6 PySpark jobs referencing script paths.
  - `aws_glue_crawler`: Automated catalog crawler.
  - `aws_iam_role`: S3 and Glue service execution policies.
- **`modules/monitoring`**: CloudWatch log retention (14 days) and job execution metrics.

## Next Reading
- [11 Configuration](11_CONFIGURATION.md)
