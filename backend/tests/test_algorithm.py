import pytest
from app.algorithm import calculate_sm2

def test_invalid_quality_rating():
    """Verify that quality scores outside 0-5 raise a ValueError."""
    with pytest.raises(ValueError):
        calculate_sm2(quality=6, repetitions=0, previous_interval=1, previous_ease_factor=2.5)
    with pytest.raises(ValueError):
        calculate_sm2(quality=-1, repetitions=0, previous_interval=1, previous_ease_factor=2.5)

def test_failed_review_resets_streak():
    """Any score < 3 must reset repetitions to 0 and set interval back to 1 day."""
    reps, interval, ease, _ = calculate_sm2(
        quality=2, 
        repetitions=5, 
        previous_interval=20, 
        previous_ease_factor=2.5
    )
    assert reps == 0
    assert interval == 1
    assert ease < 2.5  # Ease factor drops on failure

def test_successful_progression_intervals():
    """Verify standard SM-2 intervals: 1st success = 1 day, 2nd success = 6 days."""
    # First successful review
    r1, i1, e1, _ = calculate_sm2(quality=4, repetitions=0, previous_interval=0, previous_ease_factor=2.5)
    assert r1 == 1
    assert i1 == 1

    # Second consecutive successful review
    r2, i2, e2, _ = calculate_sm2(quality=4, repetitions=r1, previous_interval=i1, previous_ease_factor=e1)
    assert r2 == 2
    assert i2 == 6

    # Third review scales by ease factor
    r3, i3, e3, _ = calculate_sm2(quality=4, repetitions=r2, previous_interval=i2, previous_ease_factor=e2)
    assert r3 == 3
    assert i3 == int(round(6 * e2))

def test_ease_factor_floor():
    """Ease factor should never drop below the minimum threshold of 1.3."""
    _, _, ease, _ = calculate_sm2(quality=0, repetitions=0, previous_interval=1, previous_ease_factor=1.3)
    assert ease == 1.3
