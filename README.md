# ⚽ Multimodal Tactical RAG & Spatial Analytics Assistant

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![Apache Airflow](https://img.shields.io/badge/Airflow-Orchestration-017CEE?style=for-the-badge&logo=apache-airflow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit)

An enterprise-grade, end-to-end Data Engineering and Generative AI pipeline that bridges the gap between raw spatial match data, broadcast video, and natural language. 

This architecture introduces a **Multimodal Retrieval-Augmented Generation (RAG)** system designed for elite football tactical analysis. It translates complex spatio-temporal coordinate data and Vision Transformer (ViT) tracking into conversational insights, allowing analysts to query match events dynamically on a digital pitch.

---

## 🧠 System Architecture

The pipeline is broken down into three heavily orchestrated layers:

1. **The Data Engineering Pitch (Ingestion & ETL):**
   * **Apache Airflow** automatically extracts JSON event logs and 360-degree freeze frames from the StatsBomb Open Data API.
   * **Pydantic** enforces strict data contracts, normalizing $120 \times 80$ pitch coordinates into a standard metric grid.
   * Cleaned spatial data is staged in Parquet format and bulk-loaded into a containerized **PostgreSQL** data warehouse.

2. **The Vision Transformer Module (Spatial Tracking):**
   * Ingests open-source broadcast footage and utilizes Vision Transformers (ViT) to track player bounding boxes.
   * Applies geometric homography matrices to project 2D screen pixels onto top-down 2D tactical pitch coordinates, merging video data with textual event logs.

3. **The Multimodal RAG Engine (Generation):**
   * Tactical reports and spatial events are chunked, embedded via HuggingFace/OpenAI models, and loaded into **`pgvector`** for high-dimensional semantic search.
   * **FastAPI** serves the backend retrieval loop, fetching context-aware spatial vectors and passing them to an LLM to generate precise tactical summaries.
   * **Streamlit** & `mplsoccer` render the frontend, dynamically plotting retrieved events on a digital pitch alongside the AI-generated text.

---

## 📂 Project Structure

```text
football-multimodal-rag-analytics/
├── .env                        # Environment variables (API Keys, DB credentials)
├── docker-compose.yml          # Multi-container orchestration (Airflow, Postgres)
├── Dockerfile.airflow          # Custom Airflow image with ML dependencies
├── requirements.txt            # Python dependencies
├── config/                     # Pipeline configuration files
├── dags/                       # Apache Airflow DAGs
│   └── ingest_statsbomb_dag.py # StatsBomb extraction & validation pipeline
├── data/                       # Local data lake
│   ├── processed/              # Cleaned Parquet & embeddings
│   └── raw/                    # Raw JSON payloads & video clips
├── scripts/                    # Homography & CV processing scripts
└── sql/                        # Database migrations
    └── init_pgvector.sql       # Postgres vector extension & schema initialization
