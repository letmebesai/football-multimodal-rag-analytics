import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Use 'localhost' if running from your VS Code terminal, or 'postgres' if running inside a Docker container
DATABASE_URL = "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"

def normalize_coordinates(df):
    """
    StatsBomb pitch is 120x80. Standard pitch is 105x68 meters.
    Formula: X_metric = X_sb * (105/120) | Y_metric = Y_sb * (68/80)
    """
    # Normalize starting locations
    df['loc_x_metric'] = df['location_x'] * (105 / 120)
    df['loc_y_metric'] = df['location_y'] * (68 / 80)
    
    # Normalize pass end locations
    df['pass_end_x_metric'] = df['pass_end_location_x'] * (105 / 120)
    df['pass_end_y_metric'] = df['pass_end_location_y'] * (68 / 80)
    
    # Round to 2 decimal places for cleaner text synthesis
    return df.round(2)

def generate_semantic_descriptions(row):
    """
    Converts spatial data into a natural language sentence for the LLM.
    """
    base_text = f"Minute {row['minute']}:{row['second']} - {row['player_name']} ({row['team_name']}) performed a {row['event_type']} "
    
    if pd.notna(row['loc_x_metric']) and pd.notna(row['loc_y_metric']):
        base_text += f"at pitch coordinates X:{row['loc_x_metric']}m, Y:{row['loc_y_metric']}m. "
        
    if row['event_type'] == 'Pass' and pd.notna(row['pass_end_x_metric']):
        base_text += f"The pass ended at X:{row['pass_end_x_metric']}m, Y:{row['pass_end_y_metric']}m."
        
    return base_text.strip()

def run_transformation():
    print("Extracting raw events from PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    
    # Load raw data
    query = "SELECT * FROM raw_match_events WHERE location_x IS NOT NULL;"
    df = pd.read_sql(query, engine)
    
    print("Applying spatial normalization...")
    df = normalize_coordinates(df)
    
    print("Generating semantic text for RAG...")
    df['tactical_description'] = df.apply(generate_semantic_descriptions, axis=1)
    
    # Select only the columns we need for the Vector DB
    clean_df = df[['id', 'match_id', 'minute', 'second', 'team_name', 'player_name', 
                   'event_type', 'loc_x_metric', 'loc_y_metric', 'tactical_description']]
    
    print("Loading cleaned data back to PostgreSQL...")
    clean_df.to_sql("cleaned_match_events", con=engine, if_exists="replace", index=False)
    print("Day 2 Transformation Complete! ✅")

if __name__ == "__main__":
    run_transformation()