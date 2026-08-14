# Task Prompt: Terraform IaC Deployment

## Context Files to Load
Before writing or modifying Terraform IaC modules in `terraform/`, you MUST load the following knowledge files:
1. `knowledge_base/06_AWS_INFRASTRUCTURE.md`
2. `knowledge_base/10_TERRAFORM.md`
3. `knowledge_base/14_COMMON_COMMANDS.md`

## Instructions
- Keep modules modularly separated into `terraform/modules/s3`, `glue`, and `monitoring`.
- Use input variables in `variables.tf` and outputs in `outputs.tf`.
- Support environment switching (`dev`, `staging`, `prod`) via `var.environment`.
- Validate terraform changes using `terraform fmt`, `terraform validate`, and `terraform plan`.
