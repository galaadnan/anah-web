from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import pipeline
import os

app = Flask(__name__, static_folder='.')
CORS(app) 

# 1. التعديل الجوهري: التحميل من الإنترنت بدلاً من المجلد المحلي
# هذا يضمن أن الموديل كامل 100% ولا يحتاج لرفعه على GitHub
MODEL_PATH = "UBC-NLP/MARBERTv2"

# 2. تحميل الموديل
try:
    # سيقوم السيرفر بتحميل الموديل تلقائياً عند أول تشغيل
    pipe = pipeline("text-classification", model=MODEL_PATH)
    print("✅ Model loaded successfully from Hugging Face Hub")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    pipe = None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if pipe is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # إجراء التنبؤ
    result = pipe(text)[0]
    return jsonify({"mood": result['label']})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)