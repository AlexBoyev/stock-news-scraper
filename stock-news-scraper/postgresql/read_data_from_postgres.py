import os
import json
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# ─── Load env & connect ─────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / '.env')

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASS')
)
cur = conn.cursor()

# ─── Fetch & build records ──────────────────────────────────────────────────
cur.execute("""
    SELECT date, title, url, summary, source_feed
    FROM news
    ORDER BY date DESC
""")
rows = cur.fetchall()

records = []
for date, title, url, summary, source_feed in rows:
    records.append({
        'date': date.isoformat() if hasattr(date, 'isoformat') else date,
        'title': title,
        'url': url,
        'summary': summary,
        'source_feed': source_feed
    })

# ─── Write JSON export ───────────────────────────────────────────────────────
out_file = PROJECT_ROOT / 'data' / 'news.json'
out_file.parent.mkdir(exist_ok=True)

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(records)} items to {out_file}")

cur.close()
conn.close()
