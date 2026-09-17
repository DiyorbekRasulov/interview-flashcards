# TechPrep - Spaced Repetition CS Interview Engine

A full-stack technical interview preparation platform leveraging the **SuperMemo-2 (SM-2)** spaced repetition algorithm to optimize retention intervals for core computer science concepts (Operating Systems, Concurrency, Algorithms, and System Design).

## System Architecture

* **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, CSS 3D Transforms.
* **Backend:** FastAPI (Python 3.10+), SQLAlchemy ORM, Pydantic data contracts.
* **Database:** SQLite with index-optimized lookups on review schedules and categories.
* **Algorithm:** Pure SuperMemo-2 (SM-2) engine calculating variable interval progressions and dynamic ease factors.
* **Testing:** Pytest unit test coverage on SM-2 mathematical boundaries and integration testing on HTTP endpoints.

## Spaced Repetition Scheduling Engine (SM-2)

The platform evaluates user recall on a 0–5 scale and recalibrates repetition intervals dynamically:

$$EF' = EF + (0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02))$$

* $q < 3$: Consecutive repetition count resets to 0, interval drops to 1 day.
* $q \ge 3$: Interval progression scales geometrically based on the updated ease factor ($EF \ge 1.3$).

## Getting Started

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Seed database with initial technical cards
python3 -m app.seed

# Run automated test suite
pytest -v

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000