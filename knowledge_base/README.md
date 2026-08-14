# Amazon Review Analytics Platform - Knowledge Base

Welcome to the AI-first engineering knowledge base for the **Amazon Review Analytics Platform**.

## Purpose
This knowledge base is optimized for high-quality Retrieval-Augmented Generation (RAG) context loading by AI coding agents (Stitch, Antigravity) and rapid developer navigation.

## Directory Structure
```text
knowledge_base/
├── 00_PROJECT_OVERVIEW.md    # Business goals, problem statement, core RAG/ETL solution
├── 01_ARCHITECTURE.md        # High-level architecture, medallion layers, RAG flow
├── 02_REPOSITORY_STRUCTURE.md# Folder layout, component responsibilities
├── 03_TECH_STACK.md          # Big Data, AWS Glue, PySpark, ML, Streamlit, Terraform
├── 04_DATA_PIPELINE.md       # Medallion data lake (Bronze ➔ Silver ➔ Gold)
├── 05_DATASETS.md            # Metadata and review schema definitions
├── 06_AWS_INFRASTRUCTURE.md  # S3, Glue Catalog, Crawlers, Athena, CloudWatch
├── 07_GLUE_PIPELINE.md       # AWS Glue PySpark job entry script breakdown
├── 08_ML_PIPELINE.md         # Hybrid RAG (ChromaDB, BM25, RRF, Cross-Encoder, Gemini)
├── 09_STREAMLIT_OVERVIEW.md  # Streamlit frontend app architecture & theme
├── 09_STREAMLIT_PAGES.md     # Home overview, Product Search & Dashboard pages
├── 10_TERRAFORM.md           # Modular IaC configurations
├── 11_CONFIGURATION.md       # Dataset schemas, path maps, ML settings
├── 12_TESTING.md             # PyTest suite, Spark fixtures, unit/integration tests
├── 13_CODING_GUIDELINES.md   # Formatting, line limits, typing, logging conventions
├── 14_COMMON_COMMANDS.md     # CLI commands cheatsheet for tests, app, deployment
├── 15_DECISIONS.md           # Architectural Decision Log (ADL)
├── 16_TODO.md                # Tracked technical debt & roadmap
├── 17_DESIGN_SYSTEM.md       # Tokens, palette, typography, component states
├── 18_UI_COMPONENTS.md       # Reusable UI component specifications
├── 19_FRONTEND_GUIDELINES.md # Streamlit layout rules, state, accessibility
├── 20_AGENT_INDEX.md         # AI context routing index by technical domain
├── README.md                 # Primary knowledge base README
├── diagrams/                 # Mermaid visualizations (Architecture, AWS, Pipelines)
├── generated/                # Auto-generated code mappings (Functions, Classes)
└── prompts/                  # Task-specific AI prompts (Frontend, Backend, AWS, ML)
```

## How AI Agents Should Navigating This Knowledge Base
1. Open [20 Agent Index](20_AGENT_INDEX.md) to locate the exact documentation files required for your specific engineering task.
2. Read the domain-specific prompt in `knowledge_base/prompts/<domain>.md` before modifying source files.
3. Check [02 Repository Structure](02_REPOSITORY_STRUCTURE.md) and `generated/` to map functions and classes.

## Developer Maintenance Rules
- **Line Limit**: Every markdown file MUST strictly remain under 100 lines.
- **File Splitting**: If a document exceeds 100 lines, split it into logical subdocuments (e.g., `09_STREAMLIT_OVERVIEW.md`, `09_STREAMLIT_PAGES.md`).
- **Standard Template**: Every markdown document MUST contain `# Title`, `## Purpose`, `## Related Files`, `## Key Concepts`, `## Content`, and `## Next Reading`.
- **Single Source of Truth**: Never duplicate technical details across files. Link to primary files instead.
