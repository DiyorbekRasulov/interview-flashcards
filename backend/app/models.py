from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(64), index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    hint = Column(Text, nullable=True)

    # SM-2 Spaced Repetition Engine State
    repetition_count = Column(Integer, default=0, nullable=False)
    interval_days = Column(Integer, default=0, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    next_review_date = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        index=True, 
        nullable=False
    )
