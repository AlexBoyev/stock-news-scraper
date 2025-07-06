# ─── Base image ──────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ─── Set the working directory to your project root ─────────────────────────
WORKDIR /stock-news-scraper

# ─── Copy everything into the container ─────────────────────────────────────
COPY . .

# ─── Install your Python dependencies ──────────────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ─── Make the runner executable ─────────────────────────────────────────────
RUN chmod +x run_spiders.sh

# ─── Default entrypoint ────────────────────────────────────────────────────
ENTRYPOINT ["./run_spiders.sh"]
