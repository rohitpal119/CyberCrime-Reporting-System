from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

# LOAD MODELS
with open("crime_model.pkl", "rb") as f:
    crime_model = pickle.load(f)

with open("tfidf.pkl", "rb") as f:
    crime_vectorizer = pickle.load(f)

with open("url_model.pkl", "rb") as f:
    url_model = pickle.load(f)

with open("url_vectorizer.pkl", "rb") as f:
    url_vectorizer = pickle.load(f)

TRUSTED_DOMAINS = [
    "google.com","youtube.com","gmail.com","github.com",
    "stackoverflow.com","wikipedia.org","amazon.com",
    "microsoft.com","chatgpt.com"
]

def clean_text(text):
    text = text.lower()
    return re.sub(r'[^a-z\s]', '', text)

@app.route("/")
def home():
    return "CyberSafe AI Backend Running"

# TEXT CRIME
@app.route("/predict", methods=["POST"])
def predict_crime():
    text = request.json.get("text","")
    vec = crime_vectorizer.transform([clean_text(text)])
    pred = crime_model.predict(vec)[0].strip()
    return jsonify({"predicted_crime": pred})

# IMAGE CRIME
@app.route("/predict_image", methods=["POST"])
def predict_image():
    img = Image.open(request.files["image"])
    text = pytesseract.image_to_string(img)
    vec = crime_vectorizer.transform([clean_text(text)])
    pred = crime_model.predict(vec)[0].strip()
    return jsonify({"predicted_crime": pred})

# URL
@app.route("/predict_url", methods=["POST"])
def predict_url():
    url = request.json.get("url","")

    for d in TRUSTED_DOMAINS:
        if d in url:
            return jsonify({"threat_level":"Safe"})

    vec = url_vectorizer.transform([url])
    pred = url_model.predict(vec)[0]
    return jsonify({"threat_level": pred})

# EMAIL
@app.route("/predict_email", methods=["POST"])
def predict_email():
    email = request.json.get("email","")
    vec = crime_vectorizer.transform([clean_text(email)])
    pred = crime_model.predict(vec)[0].strip()
    threat = "Malicious" if pred=="Phishing" else "Safe"
    return jsonify({"email_threat": threat})

if __name__=="__main__":
    app.run(debug=True)
