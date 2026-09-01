import os
import pandas as pd
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from pgvector.sqlalchemy import VECTOR
from dotenv import load_dotenv

# Load environment variables from the local .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def generate_and_store_embeddings():
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL is missing. Please add it to your .env file.")
        
    print("🔄 Connecting to Neon PostgreSQL database...")
    engine = create_engine(DATABASE_URL)
    
    # Load normalized events from Day 2
    query = "SELECT * FROM cleaned_match_events LIMIT 500;"
    df = pd.read_sql(query, engine)
    
    if df.empty:
        print("⚠️ No data found in cleaned_match_events! Ensure Day 2 script ran successfully.")
        return

    print("🤖 Loading lightweight embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"📊 Generating vector embeddings for {len(df)} tactical events...")
    texts = df['tactical_description'].tolist()
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Attach embeddings to dataframe
    df['embedding'] = list(embeddings)
    
    # Select columns matching our schema
    vector_df = df[['id', 'match_id', 'minute', 'second', 'team_name', 'player_name', 
                    'event_type', 'tactical_description', 'embedding']]
    
    print("☁️ Uploading vectorized events to cloud database...")
    vector_df.to_sql("tactical_vectors", con=engine, if_exists="replace", index=False,
                     dtype={'embedding': VECTOR(384)})
    print("🚀 Day 3 Vectorization Complete!")

if __name__ == "__main__":
    generate_and_store_embeddings()