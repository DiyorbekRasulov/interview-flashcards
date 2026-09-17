from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class CardBase(BaseModel):
    category: str = Field(..., example="Operating Systems")
    question: str = Field(..., example="What is a mutex?")
    answer: str = Field(..., example="A mutual exclusion lock that allows only one thread to access a critical section.")
    hint: Optional[str] = Field(None, example="Short for mutual exclusion.")

class CardCreate(CardBase):
    pass

class CardResponse(CardBase):
    id: int
    repetition_count: int
    interval_days: int
    ease_factor: float
    next_review_date: datetime

    class Config:
        from_attributes = True

class ReviewSubmission(BaseModel):
    card_id: int
    quality: int = Field(..., ge=0, le=5, description="Quality rating must be an integer between 0 and 5")
