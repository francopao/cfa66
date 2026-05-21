"""
Session Manager — loads and persists user progress to data/progress.json
"""
import json
import os
from datetime import date
from typing import Dict, List, Optional
from core.sm2 import CardState, is_due_today

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "progress.json")


def _default_progress() -> dict:
    return {
        "cards": {},           # card_id -> CardState dict
        "sessions": [],        # list of {date, cards_reviewed, correct}
        "streak": 0,
        "last_study_date": "",
    }


def load_progress() -> dict:
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return _default_progress()


def save_progress(progress: dict) -> None:
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_card_state(progress: dict, card_id: str) -> CardState:
    if card_id in progress["cards"]:
        return CardState(**progress["cards"][card_id])
    return CardState(card_id=card_id)


def save_card_state(progress: dict, state: CardState) -> dict:
    progress["cards"][state.card_id] = state.__dict__
    return progress


def get_due_cards(progress: dict, all_card_ids: List[str]) -> List[str]:
    """Return card IDs that are due today (new cards first, then overdue)."""
    due = []
    new = []
    for cid in all_card_ids:
        if cid not in progress["cards"]:
            new.append(cid)
        else:
            state = CardState(**progress["cards"][cid])
            if is_due_today(state):
                due.append(cid)
    return new + due


def update_streak(progress: dict) -> dict:
    today = date.today().isoformat()
    last = progress.get("last_study_date", "")
    if last == today:
        pass  # already studied today
    elif last == (date.today().replace(day=date.today().day - 1)).isoformat() or last == "":
        progress["streak"] = progress.get("streak", 0) + 1
    else:
        progress["streak"] = 1
    progress["last_study_date"] = today
    return progress


def log_session(progress: dict, cards_reviewed: int, correct: int) -> dict:
    today = date.today().isoformat()
    progress["sessions"].append({
        "date": today,
        "cards_reviewed": cards_reviewed,
        "correct": correct,
    })
    # Keep last 90 days only
    progress["sessions"] = progress["sessions"][-90:]
    return update_streak(progress)


def get_stats(progress: dict) -> dict:
    cards = progress.get("cards", {})
    total = len(cards)
    mastered = sum(1 for c in cards.values() if c.get("interval", 1) >= 21)
    learning = sum(1 for c in cards.values() if 0 < c.get("interval", 1) < 21)
    new = 0  # will be computed at runtime based on all cards

    sessions = progress.get("sessions", [])
    total_reviewed = sum(s["cards_reviewed"] for s in sessions)
    total_correct = sum(s["correct"] for s in sessions)
    accuracy = round(total_correct / total_reviewed * 100) if total_reviewed > 0 else 0

    return {
        "total_cards_seen": total,
        "mastered": mastered,
        "learning": learning,
        "streak": progress.get("streak", 0),
        "accuracy": accuracy,
        "sessions": sessions,
    }
