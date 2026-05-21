"""
SM-2 Spaced Repetition Algorithm
Based on SuperMemo 2 algorithm — the science behind Anki.
"""
from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CardState:
    card_id: str
    easiness: float = 2.5       # E-Factor (difficulty), min 1.3
    interval: int = 1           # Days until next review
    repetitions: int = 0        # Number of successful reviews
    next_review: str = ""       # ISO date string
    last_quality: int = -1      # Last rating 0-5

    def __post_init__(self):
        if not self.next_review:
            self.next_review = date.today().isoformat()


def sm2_update(state: CardState, quality: int) -> CardState:
    """
    Update card state based on quality rating 0-5.
    0-2: Failed (reset repetitions)
    3: Passed but hard
    4: Passed normally
    5: Passed easily
    """
    quality = max(0, min(5, quality))
    state.last_quality = quality

    if quality >= 3:
        # Successful recall
        if state.repetitions == 0:
            state.interval = 1
        elif state.repetitions == 1:
            state.interval = 6
        else:
            state.interval = round(state.interval * state.easiness)

        state.repetitions += 1

        # Update easiness factor
        state.easiness = state.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        state.easiness = max(1.3, state.easiness)
    else:
        # Failed recall — reset
        state.repetitions = 0
        state.interval = 1

    next_date = date.today() + timedelta(days=state.interval)
    state.next_review = next_date.isoformat()
    return state


def is_due_today(state: CardState) -> bool:
    """Check if a card is due for review today or overdue."""
    return state.next_review <= date.today().isoformat()


def days_until_review(state: CardState) -> int:
    """How many days until next review (negative = overdue)."""
    review_date = date.fromisoformat(state.next_review)
    return (review_date - date.today()).days


def quality_label(q: int) -> str:
    labels = {
        0: "💀 Blackout",
        1: "😰 Wrong",
        2: "😅 Hard",
        3: "🤔 OK",
        4: "😊 Good",
        5: "🔥 Easy",
    }
    return labels.get(q, "?")
