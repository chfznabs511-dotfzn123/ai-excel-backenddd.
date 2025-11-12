# app.py - Render-ready Flask backend

from flask import Flask, request, jsonify
from flask_cors import CORS
from validator import validate_request_payload, validate_code
from runner import execute_code

app = Flask(__name__)
CORS(app)  # Allow requests from any origin

# Health check route
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Running on Render"}), 200

# Execute code endpoint
@app.route("/execute", methods=["POST"])
def execute():
    payload = request.get_json()
    errors = validate_request_payload(payload)
    if errors:
        return jsonify({"status": "error", "message": ". ".join(errors)}), 400

    code_to_run = payload["code"]
    sheet_data = payload["data"]

    code_validation_errors = validate_code(code_to_run)
    if code_validation_errors:
        return jsonify({
            "status": "error",
            "message": "Security validation failed: " + ". ".join(code_validation_errors)
        }), 400

    result = execute_code(code_to_run, sheet_data)
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500
