@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data['text']
        
        # إرسال الطلب مع تفعيل خيار الانتظار (wait_for_model)
        # هذا يمنع خطأ 502 ويجبر السيرفر ينتظر لين يصحى الموديل
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True} 
        }
        
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            # إذا استمر الخطأ، نعطي رسالة واضحة
            return jsonify({"error": "AI is waking up, try again in seconds", "details": response.text}), 502

        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            prediction = result[0][0] if isinstance(result[0], list) else result[0]
            mood = prediction.get('label', 'غير محدد')
            return jsonify({"mood": mood})
            
        return jsonify({"mood": "غير محدد"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
