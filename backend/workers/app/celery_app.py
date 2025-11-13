from celery import Celery
import os

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")

celery = Celery(
    "tasks",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/0",
    include=["app.tasks"],
)

celery.conf.update(
    task_track_started=True,
)