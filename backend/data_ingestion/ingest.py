import weaviate
import os
import pandas as pd
from datetime import datetime
import time

# --- Configuration ---
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8080")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LOG_FILE_PATH = "sample_logs/Apache_2k.log_structured.csv"
CLASS_NAME = "LogEntry"

def setup_weaviate_schema(client):
    """Sets up the Weaviate schema, configured for Google's embedding model."""
    schema = {
        "class": CLASS_NAME,
        "description": "An entry from an Apache access log",
        "vectorizer": "text2vec-google",
        "moduleConfig": {
            "text2vec-google": {
                "model": "text-embedding-004",
                "type": "text"
            }
        },
        "properties": [
            { "name": "ip_address", "dataType": ["string"] },
            { "name": "timestamp", "dataType": ["date"] },
            { "name": "log_level", "dataType": ["string"] },
            { "name": "content", "dataType": ["text"] }
        ],
    }
    # For development, we clean the schema each time to ensure consistency.
    if client.schema.exists(CLASS_NAME):
        print(f"Deleting existing schema '{CLASS_NAME}'...")
        client.schema.delete_class(CLASS_NAME)
    
    print(f"Creating schema '{CLASS_NAME}'...")
    client.schema.create_class(schema)
    print("Schema created successfully.")

def ingest_data(client):
    """Reads the structured CSV and ingests data into Weaviate."""
    print(f"Reading data from {LOG_FILE_PATH}...")
    df = pd.read_csv(LOG_FILE_PATH)
    
    client.batch.configure(batch_size=100)
    
    with client.batch as batch:
        for index, row in df.iterrows():
            try:
                ts_string = f"{row['Date']} {row['Time']}"
                timestamp = datetime.strptime(ts_string, "%Y.%m.%d %H:%M:%S")

                log_object = {
                    "ip_address": row["IP"],
                    "timestamp": timestamp.isoformat() + "Z",
                    "log_level": row["Level"],
                    "content": row["Content"]
                }
                
                batch.add_data_object(
                    data_object=log_object,
                    class_name=CLASS_NAME
                )
            except Exception as e:
                print(f"Error processing row {index}: {row}. Error: {e}")

    print(f"Data ingestion complete. Total entries processed: {len(df)}")


if __name__ == "__main__":
    # Wait for Weaviate to be ready
    time.sleep(5)
    
    print("Connecting to Weaviate...")
    client = weaviate.Client(
        url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}",
        additional_headers={"X-Google-Api-Key": GOOGLE_API_KEY},
    )
    
    setup_weaviate_schema(client)
    ingest_data(client)
    print("Ingestion script finished.")