from flask import Flask, request, jsonify
from test_project_crewai.crew import FunctionCrewServer

app = Flask(__name__)
crew_server = FunctionCrewServer()


@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    result = crew_server.process_query(query)
    return jsonify({"result": result})
