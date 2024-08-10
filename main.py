from flask import Flask, request, jsonify
from model_class import QueryRefiner, ServiceGenerator
from service_manager import ServiceManager

app = Flask(__name__)
service_manager = ServiceManager()
query_refiner = QueryRefiner(service_manager)
service_generator = ServiceGenerator(service_manager)


@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data.get("query")

    refined_result = query_refiner.refine(query)

    if refined_result["service_exists"]:
        return jsonify(refined_result)
    else:
        generator_result = service_generator.generate(
            refined_result["refined_query"], refined_result["suggested_port"]
        )
        return jsonify(generator_result)


if __name__ == "__main__":
    app.run(port=5000)
