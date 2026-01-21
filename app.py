# app.py - Main Flask application
from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)

def make_safe_response(data, status_code=200):
    """
    Wraps jsonify and adds headers to prevent Render/Proxies 
    from zipping the data, which causes the binary crash.
    """
    response = jsonify(data)
    # 'no-transform' is the critical instruction to stop zipping/compression
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, no-transform"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response, status_code

@app.route('/execute', methods=['POST'])
def execute():
    payload = request.get_json()
    errors = validate_request_payload(payload)
    if errors:
        return make_safe_response({'status': 'error', 'message': '. '.join(errors)}, 400)

    code_to_run = payload['code']
    sheet_data = payload['data']

    code_errors = validate_code(code_to_run)
    if code_errors:
        return make_safe_response({'status': 'error', 'message': 'Security validation failed: ' + '. '.join(code_errors)}, 400)

    result = execute_code(code_to_run, sheet_data)
    if result['status'] == 'success':
        return make_safe_response(result, 200)
    else:
        return make_safe_response(result, 500)

@app.route('/')
def health_check():
    return "Python Code Execution Backend is running.", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
