# AWS Infrastructure Diagram

## Purpose
Provides a visual Mermaid graph detailing managed AWS infrastructure components and connections.

## Related Files
- [06 AWS Infrastructure](../06_AWS_INFRASTRUCTURE.md)
- [10 Terraform](../10_TERRAFORM.md)

## Key Concepts
- **AWS Cloud Topology**: Integration of S3 Data Lake buckets, Glue Workflows/Jobs/Crawlers, Glue Data Catalog, Athena, and CloudWatch.

## Content

```mermaid
graph TB
    subgraph S3 Data Lake Bucket
        S3_BRONZE[/data/bronze/]
        S3_SILVER[/data/silver/]
        S3_GOLD[/data/gold/]
        S3_SCRIPTS[/scripts/]
    end

    subgraph AWS Glue Service
        GLUE_JOBS[Glue PySpark ETL Jobs]
        GLUE_WORKFLOW[Glue Workflow Scheduler]
        GLUE_CRAWLER[Glue Data Catalog Crawler]
        GLUE_CATALOG[(Glue Data Catalog DB)]
    end

    subgraph Monitoring & Analytics
        CW_LOGS[CloudWatch Log Groups]
        ATHENA[Amazon Athena Engine]
    end

    GLUE_WORKFLOW --> GLUE_JOBS
    S3_SCRIPTS --> GLUE_JOBS
    GLUE_JOBS -->|Read/Write| S3_BRONZE
    GLUE_JOBS -->|Read/Write| S3_SILVER
    GLUE_JOBS -->|Read/Write| S3_GOLD
    GLUE_JOBS -->|Execution Logs| CW_LOGS
    GLUE_CRAWLER -->|Scan| S3_GOLD
    GLUE_CRAWLER -->|Update Schema| GLUE_CATALOG
    ATHENA -->|Query| GLUE_CATALOG
```

## Next Reading
- [06 AWS Infrastructure](../06_AWS_INFRASTRUCTURE.md)
