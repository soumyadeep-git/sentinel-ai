from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

# This is a duplicate of the schemas in the API service.
# In a larger project, this would be in a shared library.
Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    status = Column(SQLAlchemyEnum(TaskStatus), default=TaskStatus.PENDING)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())