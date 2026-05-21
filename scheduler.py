"""
Content Loader — reads all formula/concept/exercise YAML files
and returns unified card objects.
"""
import yaml
import os
from typing import List, Dict, Any

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")


def _load_yaml(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else []


def load_all_cards() -> List[Dict]:
    """Load all flashcard-style items (formulas + concepts)."""
    cards = []
    for subdir in ["formulas", "concepts"]:
        folder = os.path.join(CONTENT_DIR, subdir)
        if not os.path.exists(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".yaml"):
                items = _load_yaml(os.path.join(folder, fname))
                for item in items:
                    item["_source"] = subdir
                    item["_file"] = fname.replace(".yaml", "")
                cards.extend(items)
    return cards


def load_all_exercises() -> List[Dict]:
    """Load all exercise items."""
    exercises = []
    folder = os.path.join(CONTENT_DIR, "exercises")
    if not os.path.exists(folder):
        return []
    for fname in sorted(os.listdir(folder)):
        if fname.endswith(".yaml"):
            items = _load_yaml(os.path.join(folder, fname))
            for item in items:
                item["_file"] = fname.replace(".yaml", "")
            exercises.extend(items)
    return exercises


def get_card_by_id(card_id: str, all_cards: List[Dict]) -> Dict:
    for c in all_cards:
        if c["id"] == card_id:
            return c
    return {}


def get_cards_by_topic(topic: str, all_cards: List[Dict]) -> List[Dict]:
    return [c for c in all_cards if c.get("topic", "").lower() == topic.lower()]


def get_topics(all_cards: List[Dict]) -> List[str]:
    return sorted(set(c.get("topic", "Unknown") for c in all_cards))
