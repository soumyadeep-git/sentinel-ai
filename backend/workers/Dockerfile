FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# Start Celery worker
CMD ["celery", "-A", "app.celery_app:celery", "worker", "--loglevel=info"]