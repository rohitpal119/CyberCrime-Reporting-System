import pandas as pd
import re
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

df = pd.read_excel("cybercrime.xlsx")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df["clean_text"] = df["complaint_text"].apply(clean_text)

df.to_csv("cybercrime_cleaned.csv", index=False, encoding="utf-8")

print("✅ Preprocessing complete. Saved as cybercrime_cleaned.csv")
