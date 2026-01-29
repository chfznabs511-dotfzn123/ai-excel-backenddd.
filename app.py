# app.py - Main Flask application and API endpoints

import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)

def sanitize_json(obj):
    """
    Recursively replaces NaN, Infinity, and -Infinity with None (null in JSON).
    This ensures the JSON output is strictly valid and won't crash the frontend.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return obj

@app.route('/execute', methods=['POST'])
def execute():
    try:
        payload = request.get_json()
        
        # 1. Input Validation
        if not payload:
             return jsonify({'status': 'error', 'message': 'Empty payload'}), 400
             
        errors = validate_request_payload(payload)
        if errors:
            return jsonify({'status': 'error', 'message': '. '.join(errors)}), 400

        code_to_run = payload.get('code')
        sheet_data = payload.get('data')

        # 2. Security Validation
        code_errors = validate_code(code_to_run)
        if code_errors:
            return jsonify({'status': 'error', 'message': 'Security validation failed: ' + '. '.join(code_errors)}), 400

        # 3. Execution
        result = execute_code(code_to_run, sheet_data)
        
        # 4. Sanitation (The Fix)
        # We clean the result before sending it to ensure no NaNs reach the frontend
        cleaned_result = sanitize_json(result)

        if cleaned_result.get('status') == 'success':
            return jsonify(cleaned_result), 200
        else:
            return jsonify(cleaned_result), 500

    except Exception as e:
        # Catch-all to ensure we always return JSON, not HTML (which causes Unexpected Token <)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def health_check():
    return "Python Code Execution Backend is running.", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
