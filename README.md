# 🚀 Amazon Review Analytics Platform

An enterprise-scale **Hybrid Retrieval-Augmented Generation (Hybrid RAG)** platform for intelligent product search using the **Amazon Reviews 2023** dataset. The platform combines large-scale data engineering, Natural Language Processing (NLP), semantic search, and Large Language Models (LLMs) to deliver context-aware product recommendations.

---

## 📌 Project Overview

This project processes Amazon product metadata and customer reviews to build a searchable AI knowledge base. Users can ask natural language questions and receive explainable product recommendations enriched with review summaries, sentiment analysis, ratings, and product information.

---

## ✨ Key Features

- Hybrid RAG-based Product Search
- Semantic Search using FAISS
- Keyword Search using BM25 / TF-IDF
- Sentiment Analysis with BERT
- Topic Modelling using BERTopic
- AI-powered Review Summarization
- Streamlit-based Interactive Dashboard
- Automated CI/CD Deployment on AWS

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Programming | Python, SQL |
| Data Engineering | PySpark, Databricks, AWS Glue |
| Cloud | AWS S3, Amazon ECS, Amazon ECR |
| AI / NLP | BERT, DistilBERT, BERTopic, MiniLM, Qwen 3.5 |
| Retrieval | FAISS, BM25, TF-IDF |
| Frontend | Streamlit |
| Monitoring | LangSmith, Prometheus, Grafana |
| DevOps | Docker, GitHub Actions |

---

## 🏗️ Architecture

```
Amazon Reviews Dataset
        │
        ▼
Amazon S3
        │
        ▼
PySpark + AWS Glue
        │
        ▼
Data Cleaning & Feature Engineering
        │
        ▼
Embeddings + FAISS Vector Store
        │
        ▼
Hybrid Retrieval (Semantic + Keyword)
        │
        ▼
Qwen LLM
        │
        ▼
Streamlit Web Application
```

---

## 🔄 Data Pipeline

1. Data Collection
2. Data Integration & Cleaning
3. NLP & Sentiment Analysis
4. Semantic Chunking
5. Embedding Generation
6. FAISS Vector Index
7. Query Embedding
8. Hybrid Retrieval
9. Prompt Augmentation
10. LLM Response Generation

---

## 📂 Repository Structure

```text
amazon-review-analytics-platform/
├── config/
├── notebooks/
├── src/
├── local-jupyter-notebook-analysis/
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 📊 Dataset

**Source:** McAuley-Lab Amazon Reviews 2023

**Categories**
- Sports & Outdoors
- Musical Instruments
- Appliances
- Video Games

---

## 🚀 Future Enhancements

- Multi-modal (Image + Text) Search
- Real-time Data Ingestion
- User Feedback Loop
- Domain-specific LLM Fine-tuning

---

## 👥 Team

**Group 2 – Big Data & AI Systems**

- Mohammed Affaan Arbani
- Shreyash Sanjay Dongare
- Akshata Shivram Gawade
- Ankit Kumar
- Sankalp Suresh Deore
- Yashvardhan Sahu
- Abhijeet Soni
- Kinjal Ramdas Bopte
- Vishal Deepak Jadhav

---

## 📜 License

This project is developed for academic and educational purposes.
