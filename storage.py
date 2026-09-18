import json
import os
from typing import List
from models import Joke

class HistoryStorage:
    def __init__(self, filename="saved_jokes.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_jokes(self) -> List[Joke]:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Joke.from_dict(item) for item in data]
        except Exception:
            return []

    def save_joke(self, joke: Joke) -> bool:
        jokes = self.load_jokes()
        if any(j.item_id == joke.item_id for j in jokes):
            return False  # Avoid duplicates
        
        jokes.append(joke)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([j.to_dict() for j in jokes], f, ensure_ascii=False, indent=2)
        return True

    def delete_joke(self, index: int) -> bool:
        jokes = self.load_jokes()
        if 0 <= index < len(jokes):
            jokes.pop(index)
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([j.to_dict() for j in jokes], f, ensure_ascii=False, indent=2)
            return True
        return False

    def filter_by_category(self, category: str) -> List[Joke]:
        jokes = self.load_jokes()
        return [j for j in jokes if j.category.lower() == category.lower()]