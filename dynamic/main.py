from flask import Flask, request, jsonify
from flask_cors import CORS
from query_refiner import QueryRefiner
from service_generator import ServiceGenerator
from service_manager import ServiceManager

app = Flask(__name__)
CORS(app)
service_manager = ServiceManager()
query_refiner = QueryRefiner(service_manager)
service_generator = ServiceGenerator(service_manager)


@app.route("/query", methods=["POST"])
def handle_query():
    query = request.json.get("query", "")
    refiner_result = query_refiner.refine(query)

    if refiner_result["service_exists"]:
        return jsonify(refiner_result)
    else:
        print(refiner_result)
        generator_result = service_generator.generate(
            refiner_result["refined_query"],
            refiner_result["suggested_port"],
            refiner_result["needs_json_data"],
            refiner_result.get("json_data_info"),
            refiner_result["http_method"],
        )
        return jsonify(generator_result)


if __name__ == "__main__":
    app.run(port=5000)