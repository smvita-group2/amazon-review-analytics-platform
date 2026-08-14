# Pipeline Diagram

## Purpose
Provides a Mermaid flowchart illustrating the Medallion Data Lake transformation flow.

## Related Files
- [04 Data Pipeline](../04_DATA_PIPELINE.md)
- [07 Glue Pipeline](../07_GLUE_PIPELINE.md)

## Key Concepts
- **Data Pipeline Progression**: Sequential transformation from raw JSON files to Silver cleaned master datasets to Gold analytical tables.

## Content

```mermaid
flowchart LR
    subgraph Bronze
        RAW_META[meta_*.json.gz]
        RAW_REV[reviews_*.json.gz]
    end

    subgraph Silver
        GLUE_META[bronze_to_silver_metadata]
        GLUE_REV[bronze_to_silver_reviews]
        SILVER_MASTER[silver_master_glue]
    end

    subgraph Gold
        GOLD_VIZ[gold_visualization]
        GOLD_AGG[gold_aggregates]
        GOLD_ML[gold_ml_hybrid_cleaned]
    end

    RAW_META --> GLUE_META
    RAW_REV --> GLUE_REV
    GLUE_META --> SILVER_MASTER
    GLUE_REV --> SILVER_MASTER
    SILVER_MASTER --> GOLD_VIZ
    SILVER_MASTER --> GOLD_AGG
    SILVER_MASTER --> GOLD_ML
```

## Next Reading
- [04 Data Pipeline](../04_DATA_PIPELINE.md)
