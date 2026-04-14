from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from backend.model import predict_scam
from deep_translator import GoogleTranslator # pyright: ignore[reportMissingImports]

app = Flask(__name__)
CORS(app)

translator = GoogleTranslator()

SCAM_KEYWORDS = [
    "urgent",
    "bank blocked",
    "verify",
    "verify now",
    "click now",
    "click here",
    "lottery",
    "winner",
    "free gift",
    "free money",
    "account suspended",
    "account blocked",
    "update kyc",
    "kyc",
    "otp",
    "password",
    "credit card",
    "debit card",
    "claim now",
    "reward",
    "prize"
]

SUSPICIOUS_DOMAINS = [
    "bit.ly",
    "tinyurl.com",
    "goo.gl",
    "t.co",
    "rb.gy"
]

TRANSLATIONS = {
    "en": {
        "safe": "Safe Message",
        "suspicious": "Suspicious Message",
        "danger": "Dangerous Message",
        "probability": "Scam Probability",
        "keywords": "Keywords",
        "links": "Links"
    },
    "hi": {
        "safe": "संदेश सुरक्षित है",
        "suspicious": "संदेश संदिग्ध है",
        "danger": "संदेश खतरनाक है",
        "probability": "धोखाधड़ी की संभावना",
        "keywords": "कीवर्ड",
        "links": "लिंक"
    },
    "mr": {
        "safe": "संदेश सुरक्षित आहे",
        "suspicious": "संदेश संशयास्पद आहे",
        "danger": "संदेश धोकादायक आहे",
        "probability": "फसवणुकीची शक्यता",
        "keywords": "कीवर्ड",
        "links": "लिंक्स"
    }
}
@app.route("/")
def home():
    return "Scam Detector API Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    original_message = (data.get("message") or "").strip()
    lang = (data.get("lang") or "en").strip() or "en"

    # 🌐 STEP 1: DETECT + TRANSLATE INPUT
    detected_lang = "unknown"
    translated_input = original_message

    if original_message:
        try:
            detected = translator.detect(original_message)
            detected_lang = getattr(detected, "lang", "unknown") or "unknown"

            if detected_lang != "en":
                translated_input = translator.translate(original_message, dest="en").text
        except Exception as err:
            app.logger.debug(f"Translation input failed: {err}")
            detected_lang = "unknown"
            translated_input = original_message

    message = translated_input.lower()

    found_keywords = []
    found_links = []
    suspicious_links = []

    # KEYWORDS
    for keyword in SCAM_KEYWORDS:
        if keyword in message:
            found_keywords.append(keyword)
    

    # LINKS
    url_pattern = r'(https?://\S+)'
    links = re.findall(url_pattern, message)

    for link in links:
        found_links.append(link)
        for domain in SUSPICIOUS_DOMAINS:
            if domain in link:
                suspicious_links.append(link)

    # =========================
    # SCAM PROBABILITY
    # =========================
    scam_probability = 0

    # 🚨 STEP 3: strong keyword rule
    if len(found_keywords) >= 2:
        scam_probability += 30
        # ⚠️ STEP 3.5: medium keyword rule
    elif len(found_keywords) == 1:
        scam_probability += 20

    # AI MODEL
    prediction, ai_probability = predict_scam(message)
    ai_score = int(ai_probability * 100)

    scam_probability += ai_score * 0.4

    # keyword weight
    scam_probability += len(found_keywords) * 25

    # link weight
    scam_probability += len(found_links) * 5

    # suspicious link weight
    scam_probability += len(suspicious_links) * 20

    # cap
    scam_probability = min(int(scam_probability), 100)

    # 🚨 STEP 5: threshold fix
    if len(found_keywords) >= 2 and scam_probability < 50:
        scam_probability = 50
    

    # RESULT (FIXED)
    if scam_probability < 30:
        result_key = "safe"
    elif scam_probability < 70:
        result_key = "suspicious"
    else:
        result_key = "danger"

    # 🌐 STEP 2: TRANSLATE OUTPUT (ROBUST)
    lang_data = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    translated_result = lang_data[result_key]

    result = {
        "original_message": original_message,
        "translated_input": translated_input,
        "detected_language": detected_lang,
        "scam_probability": scam_probability,

        "keywords_found": found_keywords,
        "links_found": found_links,

        "result_text": translated_result,
        "result_key": result_key,   # IMPORTANT (for frontend color)

        "labels": {
            "probability": lang_data["probability"],
            "keywords": lang_data["keywords"],
            "links": lang_data["links"]
        }
    }

    return jsonify(result)

#if __name__ == "__main__":
#    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)