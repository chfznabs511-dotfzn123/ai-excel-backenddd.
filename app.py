# app.py - Render-ready Flask backend

from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)  # Allow requests from any origin

# --- THE 100% FIX: Helper function to disable compression ---
def make_safe_response(data, status_code=200):
    """
    Wraps jsonify and adds headers to FORCE the server (Render)
    to send raw text. This prevents the binary/compression error.
    """
    response = jsonify(data)
    # "no-transform" commands Render: "Do not zip or modify this file"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, no-transform"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response, status_code
# ------------------------------------------------------------

# Health check route
@app.route("/", methods=["GET"])
def health_check():
    return make_safe_response({"status": "Running on Render"})

# Execute code endpoint
@app.route("/execute", methods=["POST"])
def execute():
    payload = request.get_json()
    
    # 1. Validate Payload
    errors = validate_request_payload(payload)
    if errors:
        return make_safe_response({"status": "error", "message": ". ".join(errors)}, 400)

    code_to_run = payload["code"]
    sheet_data = payload["data"]

    # 2. Validate Code Security
    code_validation_errors = validate_code(code_to_run)
    if code_validation_errors:
        return make_safe_response({
            "status": "error",
            "message": "Security validation failed: " + ". ".join(code_validation_errors)
        }, 400)

    # 3. Execute Code
    result = execute_code(code_to_run, sheet_data)
    
    if result["status"] == "success":
        return make_safe_response(result, 200)
    else:
        return make_safe_response(result, 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
