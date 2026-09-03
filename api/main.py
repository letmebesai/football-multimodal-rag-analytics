import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Football Tactical RAG API")
model = SentenceTransformer('all-MiniLM-L6-v2')
engine = create_engine(DATABASE_URL)

# Initialize the LLM
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm = genai.GenerativeModel('gemini-2.5-flash')

class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 3

@app.post("/search")
def semantic_search(request: QueryRequest):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="Database URL not configured.")
        
    try:
        query_vector = model.encode(request.prompt).tolist()
        
        sql = text("""
            SELECT match_id, minute, second, player_name, tactical_description, 
                   1 - (embedding <=> CAST(:query_vector AS vector)) AS similarity 
            FROM tactical_vectors 
            ORDER BY embedding <=> CAST(:query_vector AS vector) 
            LIMIT :top_k;
        """)
        
        with engine.connect() as conn:
            result = conn.execute(sql, {"query_vector": str(query_vector), "top_k": request.top_k})
            matches = [{"time": f"{row[1]}:{row[2]}", "player": row[3], "description": row[4], "confidence_score": round(row[5], 4)} for row in result]
            
        # The "G" in RAG: LLM Synthesis
        llm_summary = "LLM API Key missing from .env"
        if GEMINI_API_KEY and matches:
            context = "\n".join([m["description"] for m in matches])
            prompt = f"Act as an elite football tactical analyst. Based ONLY on these retrieved spatial events, write a concise, professional 3-sentence summary of the tactical intent. \n\nEvents:\n{context}\n\nQuery: {request.prompt}"
            
            response = llm.generate_content(prompt)
            llm_summary = response.text

        return {"query": request.prompt, "results": matches, "llm_summary": llm_summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))