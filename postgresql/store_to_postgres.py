# postgresql/store_to_postgres.py

import os
import json
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Determine project root (one level up from this script)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / '.env')

# Database connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS')
)
cur = conn.cursor()

# Path to JSON data file (bind-mounted into container)
JSON_DIR = PROJECT_ROOT / 'data'
JSON_FILE = JSON_DIR / 'news.json'

# Ensure the data directory exists
JSON_DIR.mkdir(parents=True, exist_ok=True)
# If no JSON file, initialize it to an empty array
if not JSON_FILE.exists():
    JSON_FILE.write_text('[]', encoding='utf-8')
    print(f"Initialized new JSON file at {JSON_FILE}")
else:
    print(f"Loading data from {JSON_FILE} into Postgres...")

# Upsert function

def load_and_upsert(file_path, table):
    with open(file_path, encoding='utf-8') as f:
        text = f.read().strip()
    try:
        items = json.loads(text)
    except json.JSONDecodeError:
        items = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                items.append(obj)
            except json.JSONDecodeError:
                continue

    for it in items:
        cur.execute(
            f"""
            INSERT INTO {table} (date, title, url, summary, source_feed)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            """,
            (
                it.get('date'),
                it.get('title'),
                it.get('url'),
                it.get('summary'),
                it.get('source_feed'),
            )
        )
    conn.commit()

# Execute upsert
load_and_upsert(JSON_FILE, 'news')
print("Upsert complete.")

# Close connections
cur.close()
conn.close()
