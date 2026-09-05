# ⚽ Multimodal Tactical RAG: Cloud-Native Football Analytics

An enterprise-grade Retrieval-Augmented Generation (RAG) pipeline that transforms raw spatial football data into interactive tactical insights. Built using StatsBomb open data (2022 World Cup Final), this cloud-native application combines semantic vector search with generative AI to analyze and visualize player movements dynamically.

## ✨ Key Features
* **Semantic Spatial Search:** Query tactical scenarios (e.g., "Mbappe attacking the box") using natural language.
* **Cloud-Native Vector Database:** Utilizes Neon Serverless PostgreSQL with `pgvector` for high-speed cosine similarity retrieval.
* **Generative Tactical Synthesis:** Integrates Google's Gemini 2.5 API to generate professional, context-aware tactical summaries on the fly.
* **Dynamic Pitch Mapping:** Renders retrieved spatial event coordinates directly onto a digital pitch using `mplsoccer`.

## 🛠️ Technology Stack
* **Data & AI:** Python 3.10, SentenceTransformers (`all-MiniLM-L6-v2`), Google Gemini 2.5 API
* **Database:** Neon PostgreSQL, `pgvector`, SQLAlchemy
* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit, Matplotlib, `mplsoccer`

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/letmebesai/football-multimodal-rag-analytics.git](https://github.com/letmebesai/football-multimodal-rag-analytics.git)
cd football-multimodal-rag-analytics