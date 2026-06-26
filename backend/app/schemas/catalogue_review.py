from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ModelReviewBase(BaseModel):
    model_id: Optional[str] = None
    model_version: Optional[str] = None
    assigned_reviewer_id: Optional[str] = None
    comments: Optional[str] = None

class ModelReviewSubmit(ModelReviewBase):
    pass

class ModelReviewDecision(BaseModel):
    decision: str
    comments: str

class ModelReviewInDB(ModelReviewBase):
    review_id: str
    submitted_by: str
    submitted_at: datetime
    status: str
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
