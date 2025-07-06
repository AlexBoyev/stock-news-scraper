# 📈 Stock News Scraper

A Dockerized Python-based news scraping pipeline that collects real-time financial headlines and stores them in PostgreSQL *and* locally for quick inspection.

## 📂 Project Structure

```
stock-news-scraper/
├── data/
│   └── news.json               # Latest scraped output JSON file
├── Docker/
│   ├── Dockerfile              # Production Docker build for scraper
│   └── requirements.txt        # Runtime Python dependencies
├── postgresql/
│   ├── init.sql                # Database schema and setup
│   ├── read_data_from_postgres.py
│   └── store_to_postgres.py
├── stock_scraper/
│   ├── spiders/                # Scrapy spiders for each feed/source
│   ├── items.py
│   └── settings.py
├── run_spiders.sh              # Entrypoint script to launch all scrapers
├── .env                        # Environment variables (e.g. list of tickers)
├── docker-compose.yml          # Defines multi-service stack (scraper + Postgres)
├── requirements.txt            # Full environment dependencies (runtime)
└── README.md                   # ← You are here!
```

## 🚀 Features

- **Multiple RSS sources**: Polls Top Stories, Realtime Headlines, Market Bulletins, and more.  
- **Extensible spiders**: Easily add new sources under `stock_scraper/spiders/`.  
- **Docker-Compose stack**: One-command bring-up for scraper + PostgreSQL.  
- **Automated storage**: Parsed items are inserted into PostgreSQL.  
- **Local JSON backup**: Scraped headlines also saved to `data/news.json`.

## 💻 Prerequisites

- Docker & Docker Compose  
- Python 3.12+  
- A Python virtual environment (recommended)

## 🔧 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/AlexBoyev/stock-news-scraper.git
   cd stock-news-scraper
   ```

2. **Set up a Python virtual environment**  
   ```bash
   python -m venv .venv
   # Activate it:
   source .venv/bin/activate    # Linux/macOS
   .\.venv\Scripts\activate  # Windows PowerShell
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**  
   - Copy `.env.example` (if provided) to `.env`  
   - Edit `.env` to define your list of tickers, database credentials, etc.

5. **Launch with Docker Compose**  
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   docker-compose logs -f scraper
   ```

6. **Inspect Data**  
   - **PostgreSQL**:  
     ```bash
     docker exec -it <postgres_container> psql -U $POSTGRES_USER -d $POSTGRES_DB
     SELECT * FROM headlines LIMIT 10;
     ```  
   - **Local JSON**:  
     ```bash
     cat data/news.json
     ```

## 📝 Adding a New Spider

1. Create a new Python module under `stock_scraper/spiders/`.  
2. Subclass `scrapy.Spider` and define your `start_urls`.  
3. Update `run_spiders.sh` to include your spider name.  
4. Rebuild or restart your Docker container.

## 🤝 Contributing

- Fork the project  
- Create a feature branch  
- Submit a pull request with tests and documentation updates  

## 📄 License

MIT © Your Name
