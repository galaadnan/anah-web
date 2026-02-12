from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# رابط الموديل على Hugging Face
API_URL = "https://api-inference.huggingface.co/models/UBC-NLP/MARBERTv2"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        
        # إرسال الطلب لـ Hugging Face API
        response = requests.post(API_URL, json={"inputs": text}, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": "AI Service Unavailable", "details": response.text}), 502

        result = response.json()
        
        # استخراج النتيجة (Mood)
        if isinstance(result, list) and len(result) > 0:
            # نتعامل مع هيكل البيانات العائد من MARBERTv2
            prediction = result[0][0] if isinstance(result[0], list) else result[0]
            mood = prediction.get('label', 'غير محدد')
            return jsonify({"mood": mood})
            
        return jsonify({"mood": "غير محدد"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
