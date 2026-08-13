# 00 Project Overview

## Purpose

The **Amazon Review Analytics Platform** is an intelligent product search and analytics platform that transforms raw e-commerce metadata and customer reviews into actionable insights and conversational answers.

## Business Problem

When shopping online, users struggle with:
- Manually reading hundreds of customer reviews across multiple product pages.
- Standard search engines failing on complex natural language queries.
- Disconnect between lexical (keyword) match and semantic intent.
- Comparing customer feedback trends across multiple product variants.

## Core Solution

A hybrid retrieval-augmented generation (RAG) system combined with an automated big data ETL pipeline:
1. **Medallion Data Lake**: Scalable ingestion & cleaning of Amazon dataset using AWS Glue & PySpark.
2. **Hybrid RAG Engine**: Combines vector semantic search (SentenceTransformers + ChromaDB) with keyword search (BM25), fused via Reciprocal Rank Fusion (RRF) and re-ranked with Cross-Encoder models.
3. **Generative AI Response**: Grounds user prompts in factual product reviews using Google Gemini LLM.
4. **Interactive BI & Dashboard**: Streamlit interface and Athena/Power BI integrations for visual review analytics.

## Core Capabilities

- **Natural Language Product Search**: Intelligent queries over product metadata and customer reviews.
- **Review Summary Generation**: AI-generated summaries of positive, negative, and key product aspects.
- **Automated Data Processing**: End-to-end Glue PySpark ETL pipeline for Bronze, Silver, and Gold datasets.
- **Infrastructure as Code**: Reproducible AWS deployment managed via Terraform.
