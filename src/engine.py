from .moderator import AIModerator
from .filter import KeywordFilter
from .config import Config

class ModerationEngine:
    def __init__(self):
        self.ai = AIModerator()
        self.filter = KeywordFilter()
        self.threshold = Config.AI_THRESHOLD

    def moderate(self, text: str) -> dict:

        if self.filter.is_flagged(text):
            return {"status": "FLAGGED", "reason": "keyword", "score": 1.0}

        score = self.ai.predict(text)
        if score >= self.threshold:
             return {"status": "FLAGGED", "reason": "ai", "score": score}

        return {"status": "CLEAN", "score": score, "reason": "none"}
