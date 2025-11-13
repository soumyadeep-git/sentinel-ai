from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
import os
from celery import Celery

# Create DB tables on startup
schemas.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Sentinel AI API")

# Celery configuration to send tasks
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = os.getenv("REDIS_PORT", "6379")
celery_app = Celery(
    "worker",
    broker=f"redis://{redis_host}:{redis_port}/0",
    backend=f"redis://{redis_host}:{redis_port}/0",
)

# Dependency to get a DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/investigate", response_model=models.InvestigationResponse)
def create_investigation(
    request: models.InvestigationRequest, db: Session = Depends(get_db)
):
    """Starts a new investigation by creating a record and dispatching a Celery task."""
    db_investigation = schemas.Investigation(query=request.query)
    db.add(db_investigation)
    db.commit()
    db.refresh(db_investigation)

    celery_app.send_task("app.tasks.run_investigation", args=[db_investigation.id])

    return db_investigation

@app.get("/investigations/{investigation_id}", response_model=models.InvestigationResponse)
def get_investigation_status(investigation_id: int, db: Session = Depends(get_db)):
    """Checks the status and result of a specific investigation."""
    db_investigation = db.query(schemas.Investigation).filter(schemas.Investigation.id == investigation_id).first()
    if db_investigation is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return db_investigation