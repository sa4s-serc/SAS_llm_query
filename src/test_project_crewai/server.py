from flask import Flask, request, jsonify
from test_project_crewai.crew import process_query
import math

app = Flask(__name__)


@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    result = process_query(query)
    return jsonify(result)
