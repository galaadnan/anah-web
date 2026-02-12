from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# 1. إعدادات الموديلات
MARBERT_URL = "https://api-inference.huggingface.co/models/UBC-NLP/MARBERTv2"
# ملاحظة: Gemini يحتاج API Key مجاني من (Google AI Studio)
GEMINI_API_KEY = "ضعي_هنا_API_KEY_الخاص_بجمناي" 
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # المحاولة الأولى: MARBERT (Hugging Face)
    try:
        response = requests.post(
            MARBERT_URL, 
            json={"inputs": text, "options": {"wait_for_model": True}}, 
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            prediction = result[0][0] if isinstance(result[0], list) else result[0]
            return jsonify({"mood": prediction.get('label', 'غير محدد'), "source": "MARBERT"})
    except:
        pass # إذا فشل MARBERT، ننتقل تلقائياً لـ Gemini

    # المحاولة الثانية: Gemini (خطة الطوارئ المستقرة)
    try:
        prompt = f"حلل مشاعر النص التالي باللغة العربية وأعطني كلمة واحدة فقط من (سعيد، حزين، غاضب، قلق، متعب، لا بأس): {text}"
        gemini_payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(GEMINI_URL, json=gemini_payload, timeout=10)
        
        if res.status_code == 200:
            gemini_result = res.json()
            mood = gemini_result['candidates'][0]['content']['parts'][0]['text'].strip()
            return jsonify({"mood": mood, "source": "Gemini"})
    except Exception as e:
        return jsonify({"error": "All services failed", "details": str(e)}), 500

    return jsonify({"mood": "غير محدد", "source": "None"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
