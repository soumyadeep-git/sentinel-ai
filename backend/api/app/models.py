from pydantic import BaseModel, ConfigDict
from typing import Optional
from .schemas import TaskStatus
import datetime

class InvestigationRequest(BaseModel):
    query: str

class InvestigationResponse(BaseModel):
    id: int
    query: str
    status: TaskStatus
    summary: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)