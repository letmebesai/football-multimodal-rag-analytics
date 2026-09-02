# ⚽ Multimodal Tactical RAG & Spatial Analytics Assistant

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql)
![Neon Cloud](https://img.shields.io/badge/Neon-Serverless-00E599?style=for-the-badge&logo=neon)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit)

An enterprise-grade, cloud-native Data Engineering and Generative AI pipeline that bridges the gap between raw spatial match data, broadcast video, and natural language 🌩️🧠. 

This architecture introduces a **Multimodal Retrieval-Augmented Generation (RAG)** system designed for elite football tactical analysis. It translates complex spatio-temporal coordinate data and Vision Transformer (ViT) tracking into conversational insights, allowing analysts to query match events dynamically on a digital pitch 📈⚽.

---

## 🧠 System Architecture

The pipeline is structured into three high-performance layers:

1. **The Cloud-Native Ingestion & ETL Layer ☁️:**
   * Direct Python scripts extract JSON event logs and 360-degree freeze frames from the StatsBomb Open Data API.
   * Coordinate transformation normalizes $120 \times 80$ pitch coordinates into a standard $105 \times 68$ metric grid.
   * Cleaned spatial data is bulk-loaded directly into a serverless **Neon PostgreSQL** data warehouse equipped with `pgvector`.

2. **The Vision Transformer Module (Spatial Tracking) 👁️:**
   * Ingests open-source broadcast footage and utilizes Vision Transformers (ViT) to track player bounding boxes.
   * Applies geometric homography matrices to project 2D screen pixels onto top-down 2D tactical pitch coordinates, merging video data with textual event logs.

3. **The Multimodal RAG Engine (Generation) ⚡:**
   * Tactical reports and spatial events are chunked, embedded via lightweight HuggingFace sentence transformers (`all-MiniLM-L6-v2`), and indexed in **`pgvector`** for high-dimensional semantic search.
   * **FastAPI** serves the backend retrieval loop, fetching context-aware spatial vectors using cosine distance and passing them to an LLM for precise tactical summaries.
   * **Streamlit** & `mplsoccer` render the frontend, dynamically plotting retrieved events on a digital pitch alongside the AI-generated text.

---

## 📂 Project Structure

```text
football-multimodal-rag-analytics/
├── .env                      # Environment variables (Neon Database URL, API Keys)
├── .env.example              # Template configuration for environment variables
├── requirements.txt          # Python dependencies (statsbombpy, sentence-transformers, pgvector)
├── config/                   # Pipeline configuration files
├── data/                     # Local data lake cache
│   ├── processed/            # Cleaned Parquet files & embeddings
│   └── raw/                  # Raw JSON payloads & video clips
├── scripts/                  # Data engineering & ML execution scripts
│   ├── ingest_direct.py      # StatsBomb cloud ingestion pipeline
│   ├── normalize_spatial_data.py # Pitch coordinate normalization & text synthesis
│   └── generate_embeddings.py    # Transformer embedding generation & pgvector sync
└── sql/                      # Database migrations & schema definitions
    └── init_pgvector.sql     # Postgres vector extension & table initialization
