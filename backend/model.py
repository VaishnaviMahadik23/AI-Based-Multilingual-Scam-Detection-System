import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import os

# ===============================
# LOAD DATASET
# ===============================
file_path = os.path.join(os.path.dirname(__file__), "spam.csv")

df = pd.read_csv(file_path, encoding="latin-1")

# Keep only required columns
df = df[['v1', 'v2']]
df.columns = ['label', 'text']

# Convert labels: ham=0, spam=1
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# ===============================
# TEXT PROCESSING
# ===============================
vectorizer = TfidfVectorizer(
    stop_words='english',
    lowercase=True
)

X = vectorizer.fit_transform(df['text'])
y = df['label']

# ===============================
# TRAIN MODEL
# ===============================
model = MultinomialNB()
model.fit(X, y)

print("✅ Model trained successfully on dataset")

# ===============================
# PREDICTION FUNCTION
# ===============================
def predict_scam(message):
    msg_vector = vectorizer.transform([message])
    prediction = model.predict(msg_vector)[0]
    probability = model.predict_proba(msg_vector)[0][1]

    return prediction, float(probability)