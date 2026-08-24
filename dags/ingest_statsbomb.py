from datetime import datetime, timedelta
import json
import pandas as pd
from sqlalchemy import create_engine
from statsbombpy import sb
from pydantic import BaseModel
from typing import Optional, List

from airflow import DAG
from airflow.operators.python import PythonOperator

DATABASE_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# Pydantic Data Contract
class FootballEventSchema(BaseModel):
    id: str
    match_id: int
    event_index: Optional[int] = None
    period: int
    timestamp: str
    minute: int
    second: int
    type: str
    player: Optional[str] = "Unknown"
    team: str
    location: Optional[List[float]] = None
    pass_end_location: Optional[List[float]] = None

def extract_and_stage_events(**kwargs):
    # La Liga match (e.g., Barcelona vs Real Madrid or 2022 World Cup Final ID: 3869685)
    target_match_id = 3869685
    print(f"Fetching event data for match_id: {target_match_id}...")
    
    events_df = sb.events(match_id=target_match_id)
    
    records = []
    for _, row in events_df.iterrows():
        loc = row.get("location") if isinstance(row.get("location"), list) else None
        pass_loc = row.get("pass_end_location") if isinstance(row.get("pass_end_location"), list) else None
        
        event_dict = {
            "id": str(row.get("id")),
            "match_id": target_match_id,
            "event_index": int(row.get("index")) if pd.notna(row.get("index")) else None,
            "period": int(row.get("period", 1)),
            "timestamp": str(row.get("timestamp")),
            "minute": int(row.get("minute", 0)),
            "second": int(row.get("second", 0)),
            "type": str(row.get("type", "Unknown")),
            "player": str(row.get("player")) if pd.notna(row.get("player")) else "Unknown",
            "team": str(row.get("team", "Unknown")),
            "location": loc,
            "pass_end_location": pass_loc
        }
        
        validated = FootballEventSchema(**event_dict)
        
        records.append({
            "id": validated.id,
            "match_id": validated.match_id,
            "event_index": validated.event_index,
            "period": validated.period,
            "timestamp": validated.timestamp,
            "minute": validated.minute,
            "second": validated.second,
            "event_type": validated.type,
            "player_name": validated.player,
            "team_name": validated.team,
            "location_x": validated.location[0] if validated.location else None,
            "location_y": validated.location[1] if validated.location else None,
            "pass_end_location_x": validated.pass_end_location[0] if validated.pass_end_location else None,
            "pass_end_location_y": validated.pass_end_location[1] if validated.pass_end_location else None,
            "raw_json": json.dumps(row.dropna().to_dict(), default=str)
        })

    df_to_load = pd.DataFrame(records)
    
    # Save local backup parquet
    parquet_path = f"/opt/airflow/data/raw/match_{target_match_id}_raw.parquet"
    df_to_load.to_parquet(parquet_path, index=False)
    print(f"Persisted {len(df_to_load)} records to {parquet_path}")

    # Load to Postgres
    engine = create_engine(DATABASE_URL)
    df_to_load.to_sql("raw_match_events", con=engine, if_exists="replace", index=False)
    print("Successfully ingested into PostgreSQL table: raw_match_events")

with DAG(
    "statsbomb_event_ingestion_v1",
    default_args=default_args,
    description="Extract and validate StatsBomb spatial event logs",
    schedule_interval=None,
    catchup=False,
) as dag:

    ingest_task = PythonOperator(
        task_id="extract_and_stage_statsbomb_events",
        python_callable=extract_and_stage_events,
    )