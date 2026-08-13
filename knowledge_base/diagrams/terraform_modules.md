# Terraform Modules Topology

```mermaid
graph TD
    ROOT[terraform/main.tf]

    subgraph S3 Module
        M_S3[modules/s3]
        BUCKET[aws_s3_bucket]
        POLICY[aws_s3_bucket_policy]
        M_S3 --> BUCKET
        M_S3 --> POLICY
    end

    subgraph Glue Module
        M_GLUE[modules/glue]
        G_DB[aws_glue_catalog_database]
        G_JOB[aws_glue_job definitions]
        G_CRW[aws_glue_crawler]
        G_IAM[aws_iam_role & policies]
        M_GLUE --> G_DB
        M_GLUE --> G_JOB
        M_GLUE --> G_CRW
        M_GLUE --> G_IAM
    end

    subgraph Monitoring Module
        M_MON[modules/monitoring]
        CW_GRP[aws_cloudwatch_log_group]
        M_MON --> CW_GRP
    end

    ROOT --> M_S3
    ROOT --> M_GLUE
    ROOT --> M_MON
    M_GLUE -.->|References Bucket Name| M_S3
```
