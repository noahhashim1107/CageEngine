## What this contains
- FastAPI app, Celery workers, RabbitMQ integration
- Unit/integration tests


## Prereqs
- Python 3.12+
- Docker + Docker Compose (optional but recommended)

## Quick start (Docker)
```bash
docker compose -f docker/docker-compose.yml up --build

API at http://localhost:8000

Docs at http://localhost:8000/docs