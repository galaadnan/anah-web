from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

# إعداد التطبيق وتحديد المجلد الحالي كمصدر للملفات الثابتة
app = Flask(__name__, static_folder='.')
CORS(app)

# 1. إعدادات الموديل (الارتباط بـ MARBERTv2 عبر Hugging Face API)
API_URL = "https://api-inference.huggingface.co/models/UBC-NLP/MARBERTv2"
# ملاحظة: إذا كان لديكِ Token من Hugging Face يمكنك وضعه هنا، وإلا سيعمل للطلبات المحدودة
headers = {} 

# 2. توجيه لفتح الصفحة الرئيسية (index.html) عند الدخول للرابط الأساسي
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 3. توجيه ذكي لفتح أي ملف HTML أو ملفات أخرى (CSS, JS, Images)
# هذا الجزء هو المسؤول عن جعل أزرار التنقل بين الصفحات تعمل بدون Error 404
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# 4. نقطة الاتصال (Endpoint) لتحليل المشاعر
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # إرسال النص للموديل واستلام النتيجة
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        
        if response.status_code != 200:
            return jsonify({"error": "AI API Error", "details": response.text}), 500

        result = response.json()
        
        # معالجة النتيجة القادمة من Hugging Face وتنسيقها للموقع
        if isinstance(result, list) and len(result) > 0:
            # استخراج التسمية (Label) ذات الاحتمالية الأعلى
            prediction = result[0][0] if isinstance(result[0], list) else result[0]
            mood = prediction.get('label', 'Unknown')
            return jsonify({"mood": mood})
        
        return jsonify({"error": "Unexpected AI response format"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # تشغيل السيرفر على المنفذ الذي يحدده Render تلقائياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
