from datetime import datetime, timedelta, timezone

def calculate_sm2(quality: int, repetitions: int, previous_interval: int, previous_ease_factor: float):
    """
    Computes SuperMemo-2 spaced repetition values.
    
    Args:
        quality: User confidence score from 0 (complete blackout) to 5 (perfect recall).
        repetitions: Consecutive successful reviews.
        previous_interval: Previous interval in days.
        previous_ease_factor: Measure of card difficulty (default baseline 2.5).

    Returns:
        tuple: (new_repetitions, new_interval, new_ease_factor, next_review_date)
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality rating must be between 0 and 5.")

    # Calculate new ease factor: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ease = previous_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, new_ease)  # SM-2 ease factor lower bound

    if quality < 3:
        new_reps = 0
        new_interval = 1
    else:
        new_reps = repetitions + 1
        if new_reps == 1:
            new_interval = 1
        elif new_reps == 2:
            new_interval = 6
        else:
            new_interval = int(round(previous_interval * new_ease))

    next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)
    return new_reps, new_interval, new_ease, next_review
