from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests # نحتاج هذه المكتبة للاتصال بالـ API
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# 1. رابط الـ API للموديل الأصلي حقكم في Hugging Face
API_URL = "https://api-inference.huggingface.co/models/UBC-NLP/MARBERTv2"
# ملاحظة: إذا كان الموديل يتطلب توكن، يمكن إضافته هنا، لكن غالباً الموديلات العامة لا تحتاجه فوراً
headers = {} 

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # 2. إرسال النص للموديل في Hugging Face بدلاً من تشغيله محلياً
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    
    if response.status_code != 200:
        return jsonify({"error": "AI API Error", "details": response.text}), 500

    # 3. معالجة النتيجة القادمة من الـ API
    result = response.json()
    # النتيجة عادة تكون قائمة داخل قائمة، نأخذ أعلى احتمال
    if isinstance(result, list) and len(result) > 0:
        mood = result[0][0]['label'] if isinstance(result[0], list) else result[0]['label']
        return jsonify({"mood": mood})
    
    return jsonify({"error": "Unexpected AI response"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
