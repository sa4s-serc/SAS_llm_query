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

    # Add token usage from query refinement
    token_usage = {
        "refiner_tokens": {
            "total": query_refiner.token_tracker.total_tokens,
            "prompt": query_refiner.token_tracker.total_prompt_tokens,
            "completion": query_refiner.token_tracker.total_completion_tokens
        }
    }

    if refiner_result["service_exists"]:
        refiner_result["token_usage"] = token_usage
        return jsonify(refiner_result)
    else:
        print(refiner_result)
        generator_result = service_generator.generate(
            refiner_result["refined_query"],
            refiner_result["needs_json_data"],
            refiner_result.get("json_data_info"),
            refiner_result["http_method"],
        )
        
        # Add token usage from both operations
        token_usage["generator_tokens"] = {
            "total": service_generator.token_tracker.total_tokens,
            "prompt": service_generator.token_tracker.total_prompt_tokens,
            "completion": service_generator.token_tracker.total_completion_tokens
        }
        token_usage["total_tokens"] = {
            "total": (query_refiner.token_tracker.total_tokens + 
                     service_generator.token_tracker.total_tokens),
            "prompt": (query_refiner.token_tracker.total_prompt_tokens + 
                      service_generator.token_tracker.total_prompt_tokens),
            "completion": (query_refiner.token_tracker.total_completion_tokens + 
                         service_generator.token_tracker.total_completion_tokens)
        }
        
        generator_result["token_usage"] = token_usage
        return jsonify(generator_result)

if __name__ == "__main__":
    app.run(port=5000)