from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import re
from PIL import Image
import pytesseract
from groq import Groq
# import google.generativeai as genai

app = Flask(__name__)
CORS(app)

import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)


# genai.configure(
#     api_key=GEMINI_API_KEY
# )
# ================= LOAD MODELS =================

# model = genai.GenerativeModel(
#     "gemini-2.0-flash"
# )

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

    vec = url_vectorizer.tran

    pred = url_model.predisform([url])ct(vec)[0]

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

    "stage": "description",

    "conversation": [],

    "description": "",

    "proof": "",

    "loss": "",

    "data": {}

}

def reset_call():

    call_memory["stage"] = "description"

    call_memory["conversation"] = []

    call_memory["description"] = ""

    call_memory["proof"] = ""

    call_memory["loss"] = ""

    call_memory["data"] = {}

# ================= AI CONVERSATION =================

# def generate_call_reply(user_input):

#     user_input = user_input.lower()

#     # STEP 0
#     if call_memory["step"] == 0:

#         call_memory["step"] = 1

#         return (
#             "Hello, this is CyberSafe helpline. "
#             "I understand your concern. "
#             "Can you briefly tell me what happened?"
#         )

#     # STEP 1
#     elif call_memory["step"] == 1:

#         call_memory["data"]["incident"] = user_input

#         call_memory["step"] = 2

#         return (
#             "Okay, thank you for explaining. "
#             "When did this incident occur?"
#         )

#     # STEP 2
#     elif call_memory["step"] == 2:

#         call_memory["data"]["time"] = user_input

#         call_memory["step"] = 3

#         return (
#             "Got it. Which platform was involved, "
#             "like WhatsApp, Instagram, Telegram, "
#             "Facebook, or email?"
#         )

#     # STEP 3
#     elif call_memory["step"] == 3:

#         call_memory["data"]["platform"] = user_input

#         call_memory["step"] = 4

#         return (
#             "Alright. Do you have any proof such as "
#             "screenshots, messages, links, or "
#             "transaction details?"
#         )

#     # STEP 4
#     elif call_memory["step"] == 4:

#         call_memory["data"]["proof"] = user_input

#         # Generate FIR report
#         call_memory["data"]["report"] = {
#             "incident": call_memory["data"].get("incident", ""),
#             "time": call_memory["data"].get("time", ""),
#             "platform": call_memory["data"].get("platform", ""),
#             "proof": call_memory["data"].get("proof", "")
#         }

#         final_message = (
#             "Thank you. Your complaint has been "
#             "successfully recorded. "
#             "Our cybercrime team will review "
#             "your report shortly."
#         )

#         call_memory["step"] = 0

#         return final_message

#     # FALLBACK
#     else:

#         reset_call()

#         return (
#             "I'm here to help. "
#             "Could you please explain your issue again?"
#         )

def generate_call_reply(user_input):

    history = ""

    for msg in call_memory["conversation"][-10:]:

        history += (
            f"{msg['sender']}: "
            f"{msg['message']}\n"
        )

    prompt = f"""
You are CyberSafe AI, a cybercrime reporting officer.

IMPORTANT RULES:

- Be professional and empathetic.
- Keep replies under 40 words.
- Ask only the most important missing information.
- Ask a maximum of 2 follow-up questions.
- Do NOT ask repeated questions.
- Collect:
  • incident
  • platform
  • proof/evidence
  • financial loss

When you have enough information, reply ONLY:

REPORT_READY

Do not add any other text.

Conversation History:

{history}

Current User Message:

{user_input}
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "You are a cybercrime reporting officer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,

            max_tokens=80

        )

        reply = response.choices[0].message.content.strip()

        # ================= REPORT GENERATION =================

        if "REPORT_READY" in reply:

            fir_prompt = f"""
Extract cybercrime FIR details from this conversation.

Conversation:

{history}

Return ONLY valid JSON.

{{
    "incident":"",
    "time":"",
    "platform":"",
    "proof":""
}}
"""

            try:

                fir_response = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=[
                        {
                            "role": "user",
                            "content": fir_prompt
                        }
                    ],

                    temperature=0.1,

                    max_tokens=200

                )

                import json

                raw_report = (
                    fir_response
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # Remove markdown wrappers

                raw_report = raw_report.replace(
                    "```json",
                    ""
                )

                raw_report = raw_report.replace(
                    "```",
                    ""
                )

                report = json.loads(raw_report)

                call_memory["data"] = {
                    "report": report
                }

                print("Generated FIR:")
                print(report)

            except Exception as e:

                print("FIR Error:", e)

                call_memory["data"] = {
                    "report": {
                        "incident": "Unknown",
                        "time": "Unknown",
                        "platform": "Unknown",
                        "proof": "Unknown"
                    }
                }

            return (
                "Thank you. Your cybercrime report "
                "has been generated and submitted "
                "successfully."
            )

        return reply

    except Exception as e:

        print("Groq Error:", e)

        return (
            "Sorry, I couldn't process that. "
            "Could you please repeat?"
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

    response = {
    "reply": reply,
    "conversation": call_memory["conversation"].copy(),
    "data": call_memory["data"]
}

# If report is finished, clear memory for next call
    if "generated and submitted successfully" in reply.lower():
        call_memory["conversation"] = []
        call_memory["data"] = {}

    return jsonify(response)

# ================= RUN SERVER =================

if __name__ == "__main__":
    app.run(debug=True)