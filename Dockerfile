# Dockerfile
FROM python:3.13.5-slim-bookworm

# Set enviroment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory 
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Command to run FastAPI server 
RUN set -eux; \
    apt-get update && apt-get install -y --no-install-recommends dos2unix && rm -rf /var/lib/apt/lists/*; \
    dos2unix /usr/local/bin/entrypoint.sh; \
    chmod +x /usr/local/bin/entrypoint.sh

# Copy app files
COPY . .

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]