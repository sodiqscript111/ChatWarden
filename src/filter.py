import re
from typing import List

class KeywordFilter:
    def __init__(self, banned_words: List[str] = None):
        if banned_words is None:
            banned_words = ["spam", "buy crypto", "free money"]
        
        escaped_words = [re.escape(w) for w in banned_words]
        self.pattern = re.compile(r'\b(' + '|'.join(escaped_words) + r')\b', re.IGNORECASE)

    def is_flagged(self, text: str) -> bool:
        return bool(self.pattern.search(text))
