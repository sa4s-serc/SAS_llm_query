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


@app.route("/sqrt/<float:number>", methods=["GET"])
def calculate_square_root(number):
    result = math.sqrt(number)
    return jsonify({"result": result})


@app.route("/prime/<int:number>", methods=["GET"])
def check_prime(number):
    if number < 2:
        is_prime = False
    else:
        is_prime = all(number % i != 0 for i in range(2, int(math.sqrt(number)) + 1))
    return jsonify({"is_prime": is_prime})


@app.route("/factorial/<int:number>", methods=["GET"])
def calculate_factorial(number):
    if number < 0:
        return jsonify({"error": "Factorial is not defined for negative numbers"}), 400
    result = math.factorial(number)
    return jsonify({"result": result})
