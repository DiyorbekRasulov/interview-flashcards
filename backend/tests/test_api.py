import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_all_cards():
    response = client.get("/api/cards/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "question" in data[0]
    assert "answer" in data[0]

def test_submit_review_success():
    # Fetch first card
    cards_res = client.get("/api/cards/all")
    card_id = cards_res.json()[0]["id"]

    # Submit a high-confidence review (quality = 5)
    payload = {"card_id": card_id, "quality": 5}
    response = client.post("/api/cards/review", json=payload)
    assert response.status_code == 200
    
    updated_card = response.json()
    assert updated_card["id"] == card_id
    assert updated_card["repetition_count"] >= 1
    assert updated_card["interval_days"] >= 1

def test_submit_review_invalid_quality():
    cards_res = client.get("/api/cards/all")
    card_id = cards_res.json()[0]["id"]

    # Quality must be between 0 and 5; 9 is invalid
    payload = {"card_id": card_id, "quality": 9}
    response = client.post("/api/cards/review", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation error)

def test_submit_review_card_not_found():
    # Card ID that doesn't exist
    payload = {"card_id": 999999, "quality": 4}
    response = client.post("/api/cards/review", json=payload)
    assert response.status_code == 404
