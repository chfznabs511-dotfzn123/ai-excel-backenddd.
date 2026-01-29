# app.py - Main Flask application and API endpoints

import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB limit


def sanitize_json(obj):
    """Make data strictly JSON-safe."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")

    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [sanitize_json(v) for v in obj]

    if hasattr(obj, "item"):  # numpy scalar
        return sanitize_json(obj.item())

    return obj


def block_binary(obj):
    """Hard-stop if binary leaks through."""
    if isinstance(obj, (bytes, bytearray)):
        raise ValueError("Binary data detected in response")

    if isinstance(obj, dict):
        for v in obj.values():
            block_binary(v)

    if isinstance(obj, (list, tuple)):
        for v in obj:
            block_binary(v)


@app.route('/execute', methods=['POST'])
def execute():
    try:
        # 1️⃣ Enforce JSON only
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 415

        payload = request.get_json(silent=True)

        if payload is None or not isinstance(payload, dict):
            return jsonify({
                'status': 'error',
                'message': 'Invalid or malformed JSON body'
            }), 400

        # 2️⃣ Payload validation
        errors = validate_request_payload(payload)
        if errors:
            return jsonify({
                'status': 'error',
                'message': '. '.join(errors)
            }), 400

        code_to_run = payload.get('code')
        sheet_data = payload.get('data')

        # 3️⃣ Security validation
        code_errors = validate_code(code_to_run)
        if code_errors:
            return jsonify({
                'status': 'error',
                'message': 'Security validation failed: ' + '. '.join(code_errors)
            }), 400

        # 4️⃣ Execute user code
        result = execute_code(code_to_run, sheet_data)

        # 🚨 BLOCK BINARY FIRST
        block_binary(result)

        # 5️⃣ Sanitize JSON
        cleaned_result = sanitize_json(result)

        return jsonify(cleaned_result), (
            200 if cleaned_result.get('status') == 'success' else 500
        )

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Python Code Execution Backend is running.'
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

