# app.py - Main Flask application and API endpoints

from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
def execute():
    payload = request.get_json()
    errors = validate_request_payload(payload)
    if errors:
        return jsonify({'status': 'error', 'message': '. '.join(errors)}), 400

    code_to_run = payload['code']
    sheet_data = payload['data']

    code_errors = validate_code(code_to_run)
    if code_errors:
        return jsonify({'status': 'error', 'message': 'Security validation failed: ' + '. '.join(code_errors)}), 400

    result = execute_code(code_to_run, sheet_data)
    if result['status'] == 'success':
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/')
def health_check():
    return "Python Code Execution Backend is running.", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
 
