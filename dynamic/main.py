from flask import Flask, request, jsonify
from flask_cors import CORS
from query_refiner import QueryRefiner
from service_generator import ServiceGenerator
from service_manager import ServiceManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
service_manager = ServiceManager()
query_refiner = QueryRefiner(service_manager)
service_generator = ServiceGenerator(service_manager)

@app.route("/query", methods=["POST"])
def handle_query():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        query = data.get("query", "")
        if not query:
            return jsonify({"error": "No query provided"}), 400

        service_name = data.get("service_name")
        logger.info(f"Received request - Query: {query}, Service Name: {service_name}")

        refiner_result = query_refiner.refine(query)
        logger.info(f"Refiner result: {refiner_result}")

        if refiner_result["service_exists"]:
            logger.info("Service already exists")
            return jsonify(refiner_result)
        else:
            logger.info("Generating new service")
            generator_result = service_generator.generate(
                refiner_result["refined_query"],
                refiner_result["needs_json_data"],
                refiner_result.get("json_data_info"),
                refiner_result["http_method"],
                service_name
            )

            if generator_result is None:
                return jsonify({"error": "Failed to generate service"}), 500

            logger.info(f"Service generated successfully: {generator_result['service_name']}")
            return jsonify(generator_result)

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)