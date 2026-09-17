from datetime import datetime, timezone
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Card
from .schemas import CardResponse, ReviewSubmission
from .algorithm import calculate_sm2

# Create SQLite database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TechPrep Spaced-Repetition Engine",
    description="A spaced repetition API tailored for computer science and technical interview prep.",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits requests from local Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/cards/due", response_model=List[CardResponse], tags=["Cards"])
def get_due_cards(db: Session = Depends(get_db)):
    """Fetch all cards due for review as of the current UTC timestamp."""
    now = datetime.now(timezone.utc)
    return db.query(Card).filter(Card.next_review_date <= now).all()

@app.get("/api/cards/all", response_model=List[CardResponse], tags=["Cards"])
def get_all_cards(db: Session = Depends(get_db)):
    """Fetch all cards regardless of due date for standard deck browsing."""
    return db.query(Card).all()

@app.post("/api/cards/review", response_model=CardResponse, tags=["Review"])
def submit_review(payload: ReviewSubmission, db: Session = Depends(get_db)):
    """
    Submits user review rating (0-5) and recalculates repetition schedule via SM-2.
    """
    card = db.query(Card).filter(Card.id == payload.card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {payload.card_id} not found."
        )

    new_reps, new_interval, new_ease, next_date = calculate_sm2(
        quality=payload.quality,
        repetitions=card.repetition_count,
        previous_interval=card.interval_days,
        previous_ease_factor=card.ease_factor,
    )

    card.repetition_count = new_reps
    card.interval_days = new_interval
    card.ease_factor = new_ease
    card.next_review_date = next_date

    db.commit()
    db.refresh(card)
    return card
