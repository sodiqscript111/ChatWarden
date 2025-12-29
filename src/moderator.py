import joblib
import re
import os


class AIModerator:
    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, 'models', 'mod_model.pkl')
        vectorizer_path = os.path.join(base_path, 'models', 'vectorizer.pkl')

        print("AI Moderator: Loading brain...")
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        print("AI Moderator: Brain loaded and ready.")

    def _clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
        text = re.sub(r'[^a-z A-Z 0-9]', '', text)
        return text.strip()

    def predict(self, text: str) -> float:
        cleaned = self._clean_text(text)
        if not cleaned:
            return 0.0

        vectorized = self.vectorizer.transform([cleaned])
        probability = self.model.predict_proba(vectorized)[0][1]
        return float(probability)