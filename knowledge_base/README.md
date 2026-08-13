# Amazon Review Analytics Platform - Knowledge Base

Centralized engineering documentation designed for developers and AI agents.

## Knowledge Base Navigation

- [00 Project Overview](00_PROJECT_OVERVIEW.md): Business goals, problem statement, and solution context.
- [01 Architecture](01_ARCHITECTURE.md): System architecture, Medallion data lake, and RAG flow.
- [02 Repository Structure](02_REPOSITORY_STRUCTURE.md): Folder layout and component responsibilities.
- [03 Tech Stack](03_TECH_STACK.md): Technologies, frameworks, and cloud services.
- [04 Data Pipeline](04_DATA_PIPELINE.md): End-to-end data processing layers.
- [05 Datasets](05_DATASETS.md): Product metadata and review schema definitions.
- [06 AWS Infrastructure](06_AWS_INFRASTRUCTURE.md): S3, Glue, Catalog, Athena, and CloudWatch topology.
- [07 Glue Pipeline](07_GLUE_PIPELINE.md): AWS Glue PySpark jobs breakdown.
- [08 ML Pipeline](08_ML_PIPELINE.md): Hybrid RAG (Embeddings, BM25, RRF, Cross-Encoder, Gemini).
- [09 Streamlit UI](09_STREAMLIT.md): Interactive user interface pages and components.
- [10 Terraform IaC](10_TERRAFORM.md): Infrastructure provisioning and state management.
- [11 Configuration](11_CONFIGURATION.md): Centralized dataset schemas, path maps, and settings.
- [12 Testing](12_TESTING.md): PyTest suite structure and test coverage.
- [13 Coding Guidelines](13_CODING_GUIDELINES.md): Code style, line limits, typing, and logging.
- [14 Common Commands](14_COMMON_COMMANDS.md): Execution cheatsheet for tests, app, and infra.
- [15 Architectural Decisions](15_DECISIONS.md): Key decisions extracted from repository.
- [16 Project TODO](16_TODO.md): Future improvements and tracked technical debt.

## Subdirectories

- [Generated Indices](generated/module_index.md): Auto-generated code mappings ([Functions](generated/functions.md), [Classes](generated/classes.md), [Dependencies](generated/dependencies.md)).
- [Diagrams](diagrams/architecture_diagram.md): Mermaid visualizations for architecture and execution flows.
- [Prompts](prompts/implement_feature.md): Reusable prompts for AI agent tasks.

## Maintenance Rules

1. Each markdown file MUST remain under 100 lines.
2. If content exceeds 100 lines, split logically into sub-documents.
3. Code changes require updating affected documentation files.
