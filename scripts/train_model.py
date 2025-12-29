import pandas as pd
import joblib
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

# 1. Load the Data
print("Loading dataset...")
df = pd.read_csv('data/train.csv')

# 2. Create the Binary Label
# If any of the toxic categories are 1, 'is_abusive' becomes 1
target_cols = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
df['is_abusive'] = df[target_cols].max(axis=1)

# 3. Simple Text Cleaning Logic
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE) # Remove URLs
    text = re.sub(r'\@\w+|\#','', text) # Remove mentions/hashtags
    text = re.sub(r'[^a-z A-Z 0-9]', '', text) # Remove special characters
    text = text.strip()
    return text

print("Cleaning text...")
df['comment_text'] = df['comment_text'].astype(str).apply(clean_text)

# 4. Vectorization (Words to Numbers)
# We use n-grams (1,2) to catch phrases like "you are" as well as single words
print("Vectorizing text (this may take a minute)...")
vectorizer = TfidfVectorizer(max_features=10000, stop_words='english', ngram_range=(1, 2))
X = vectorizer.fit_transform(df['comment_text'])
y = df['is_abusive']

# 5. Split for Validation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train the Model
# 'class_weight=balanced' is vital because most comments are clean
print("Training Logistic Regression model...")
model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X_train, y_train)

# 7. Evaluate
predictions = model.predict(X_test)
print("\n--- Model Performance ---")
print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")
print(classification_report(y_test, predictions))

# 8. Save the Artifacts
print("Saving model and vectorizer to /models...")
joblib.dump(model, 'models/mod_model.pkl')
joblib.dump(vectorizer, 'models/vectorizer.pkl')
print("Done! Your AI brain is ready.")