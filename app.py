from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)

# ================= LOAD MODELS =================

with open("crime_model.pkl", "rb") as f:
    crime_model = pickle.load(f)

with open("tfidf.pkl", "rb") as f:
    crime_vectorizer = pickle.load(f)

with open("url_model.pkl", "rb") as f:
    url_model = pickle.load(f)

with open("url_vectorizer.pkl", "rb") as f:
    url_vectorizer = pickle.load(f)

# ================= TRUSTED DOMAINS =================

TRUSTED_DOMAINS = [
    "google.com",
    "youtube.com",
    "gmail.com",
    "github.com",
    "stackoverflow.com",
    "wikipedia.org",
    "amazon.com",
    "microsoft.com",
    "chatgpt.com"
]

# ================= TEXT CLEANING =================

def clean_text(text):
    text = text.lower()
    return re.sub(r'[^a-z\s]', '', text)

# ================= HOME =================

@app.route("/")
def home():
    return "CyberSafe AI Backend Running"

# ================= TEXT CRIME =================

@app.route("/predict", methods=["POST"])
def predict_crime():

    text = request.json.get("text", "")

    vec = crime_vectorizer.transform([clean_text(text)])

    pred = crime_model.predict(vec)[0].strip()

    return jsonify({
        "predicted_crime": pred
    })

# ================= IMAGE CRIME =================

@app.route("/predict_image", methods=["POST"])
def predict_image():

    img = Image.open(request.files["image"])

    text = pytesseract.image_to_string(img)

    vec = crime_vectorizer.transform([clean_text(text)])

    pred = crime_model.predict(vec)[0].strip()

    return jsonify({
        "predicted_crime": pred
    })

# ================= URL THREAT =================

@app.route("/predict_url", methods=["POST"])
def predict_url():

    url = request.json.get("url", "")

    for d in TRUSTED_DOMAINS:
        if d in url:
            return jsonify({
                "threat_level": "Safe"
            })

    vec = url_vectorizer.transform([url])

    pred = url_model.predict(vec)[0]

    return jsonify({
        "threat_level": pred
    })

# ================= EMAIL THREAT =================

@app.route("/predict_email", methods=["POST"])
def predict_email():

    email = request.json.get("email", "")

    vec = crime_vectorizer.transform([clean_text(email)])

    pred = crime_model.predict(vec)[0].strip()

    threat = "Malicious" if pred == "Phishing" else "Safe"

    return jsonify({
        "email_threat": threat
    })

# =========================================================
# ================= VOICE CALL AGENT ======================
# =========================================================

call_memory = {
    "step": 0,
    "data": {},
    "conversation": []
}

def reset_call():

    call_memory["step"] = 0
    call_memory["data"] = {}
    call_memory["conversation"] = []

# ================= AI CONVERSATION =================

def generate_call_reply(user_input):

    user_input = user_input.lower()

    # STEP 0
    if call_memory["step"] == 0:

        call_memory["step"] = 1

        return (
            "Hello, this is CyberSafe helpline. "
            "I understand your concern. "
            "Can you briefly tell me what happened?"
        )

    # STEP 1
    elif call_memory["step"] == 1:

        call_memory["data"]["incident"] = user_input

        call_memory["step"] = 2

        return (
            "Okay, thank you for explaining. "
            "When did this incident occur?"
        )

    # STEP 2
    elif call_memory["step"] == 2:

        call_memory["data"]["time"] = user_input

        call_memory["step"] = 3

        return (
            "Got it. Which platform was involved, "
            "like WhatsApp, Instagram, Telegram, "
            "Facebook, or email?"
        )

    # STEP 3
    elif call_memory["step"] == 3:

        call_memory["data"]["platform"] = user_input

        call_memory["step"] = 4

        return (
            "Alright. Do you have any proof such as "
            "screenshots, messages, links, or "
            "transaction details?"
        )

    # STEP 4
    elif call_memory["step"] == 4:

        call_memory["data"]["proof"] = user_input

        # Generate FIR report
        call_memory["data"]["report"] = {
            "incident": call_memory["data"].get("incident", ""),
            "time": call_memory["data"].get("time", ""),
            "platform": call_memory["data"].get("platform", ""),
            "proof": call_memory["data"].get("proof", "")
        }

        final_message = (
            "Thank you. Your complaint has been "
            "successfully recorded. "
            "Our cybercrime team will review "
            "your report shortly."
        )

        call_memory["step"] = 0

        return final_message

    # FALLBACK
    else:

        reset_call()

        return (
            "I'm here to help. "
            "Could you please explain your issue again?"
        )

# ================= AI CALL ROUTE =================

@app.route("/ai_call", methods=["POST"])
def ai_call():

    data = request.json

    user_text = data.get("text", "")

    # Save User Message
    call_memory["conversation"].append({
        "sender": "User",
        "message": user_text
    })

    # Generate AI Reply
    reply = generate_call_reply(user_text)

    # Save AI Reply
    call_memory["conversation"].append({
        "sender": "AI",
        "message": reply
    })

    return jsonify({
        "reply": reply,
        "conversation": call_memory["conversation"],
        "data": call_memory["data"]
    })

# ================= RUN SERVER =================

if __name__ == "__main__":
    app.run(debug=True)