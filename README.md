# Sentinel AI

Monorepo with FastAPI backend, Celery workers, optional data ingestion, and a React frontend.

## Quickstart

1. Create environment:

```bash
cp .env .env.local || true
```

2. Build and run:

```bash
docker-compose up --build -d
```

3. Open services:
- API: http://localhost:8000/health
- Frontend: http://localhost:3000
- Weaviate: http://localhost:8080

## Local Development

- Backend API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Workers:
```bash
celery -A app.celery_app:celery_app worker --loglevel=info
```

- Frontend:
```bash
npm --prefix frontend install
npm --prefix frontend run dev
```
