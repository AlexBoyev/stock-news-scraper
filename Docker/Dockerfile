# Docker/Dockerfile

# 1. Base image
FROM python:3.12-slim

# 2. Install OS-level build dependencies for any C-extensions
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      python3-dev \
      libpq-dev \
      libxml2-dev \
      libxslt1-dev \
 && rm -rf /var/lib/apt/lists/*

# 3. Set working directory inside the container
WORKDIR /stock-news-scraper

# 4. Copy only the requirements file from the Docker folder
COPY Docker/requirements.txt ./requirements.txt

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your project (code, scripts, data folder, etc.)
COPY . .

# 7. Make your spider runner executable
RUN chmod +x run_spiders.sh

# 8. Default command
ENTRYPOINT ["./run_spiders.sh"]
