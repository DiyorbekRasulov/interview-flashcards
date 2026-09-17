from datetime import datetime, timezone
import time
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .database import engine, Base, get_db
from .models import Card
from .schemas import CardResponse, ReviewSubmission
from .algorithm import calculate_sm2

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# 1. Initialize Rate Limiter using client IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TechPrep Spaced-Repetition Engine",
    description="A hardened spaced repetition API for computer science interview prep.",
    version="1.1.0",
)

# Attach SlowAPI error handler to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Hardened CORS Configuration
# Allow local dev and production vercel domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Matches any Vercel preview/prod deployment
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Security Headers & Request Timing Middleware
@app.middleware("http")
async def add_security_headers_and_timing(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time

    # Defense-in-depth security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Process-Time-Ms"] = f"{process_time * 1000:.2f}"
    return response

# 4. Endpoints with Rate Limits

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

@app.get("/api/cards/due", response_model=List[CardResponse], tags=["Cards"])
@limiter.limit("60/minute")
def get_due_cards(request: Request, db: Session = Depends(get_db)):
    """Fetch all cards due for review as of the current UTC timestamp."""
    now = datetime.now(timezone.utc)
    return db.query(Card).filter(Card.next_review_date <= now).all()

@app.get("/api/cards/all", response_model=List[CardResponse], tags=["Cards"])
@limiter.limit("60/minute")
def get_all_cards(request: Request, db: Session = Depends(get_db)):
    """Fetch all cards regardless of due date for standard deck browsing."""
    return db.query(Card).all()

@app.post("/api/cards/review", response_model=CardResponse, tags=["Review"])
@limiter.limit("20/minute")
def submit_review(request: Request, payload: ReviewSubmission, db: Session = Depends(get_db)):
    """
    Submits user review rating (0-5) and recalculates repetition schedule via SM-2.
    Rate limited to 20 reviews per minute per client IP.
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