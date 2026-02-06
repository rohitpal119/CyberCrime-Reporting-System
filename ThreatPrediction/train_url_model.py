import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("malicious_phish.csv")

# Sample to avoid RAM overload
df = df.sample(80000, random_state=42)

# Map labels to your system
label_map = {
    "benign": "Safe",
    "defacement": "Suspicious",
    "phishing": "Malicious",
    "malware": "Malicious"
}

df["label"] = df["type"].map(label_map)

X = df["url"]
y = df["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Character-level TF-IDF (BEST for URLs)
vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(3,5))

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Logistic Regression model
model = LogisticRegression(max_iter=1000)

model.fit(X_train_vec, y_train)

# Evaluate
pred = model.predict(X_test_vec)

print("\nURL Threat Model Accuracy:", accuracy_score(y_test, pred))
print("\nClassification Report:\n")
print(classification_report(y_test, pred))

# Save model
with open("url_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("url_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\n✅ URL threat model saved.")
