import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="Football Tactical RAG API")
model = SentenceTransformer('all-MiniLM-L6-v2')
engine = create_engine(DATABASE_URL)

class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 3

@app.post("/search")
def semantic_search(request: QueryRequest):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured.")
        
    try:
        # 1. Convert user text into a 384-dimensional vector
        query_vector = model.encode(request.prompt).tolist()
        
        # 2. Query Neon PostgreSQL using pgvector cosine distance (<=>)
# 2. Query Neon PostgreSQL using pgvector cosine distance (<=>)
        sql = text("""
            SELECT match_id, minute, second, player_name, tactical_description, 
                   1 - (embedding <=> CAST(:query_vector AS vector)) AS similarity 
            FROM tactical_vectors 
            ORDER BY embedding <=> CAST(:query_vector AS vector) 
            LIMIT :top_k;
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql, {"query_vector": str(query_vector), "top_k": request.top_k})
            matches = [
                {
                    "time": f"{row[1]}:{row[2]}",
                    "player": row[3],
                    "description": row[4], 
                    "confidence_score": round(row[5], 4)
                } 
                for row in result
            ]
            
        return {"query": request.prompt, "results": matches}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))