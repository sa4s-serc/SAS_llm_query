# City Companion Builder
## Branches
- The main Application resides in the `iot_prototype` branch
- For Goal Parser evaluations in standalone, please checkout `goal_parser` branch
- Backend Generation evaluations are done in the `generation_results` branch
- For User Evaluation results refer to `human2` branch

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/IIIT-Companion.git
cd IIIT-Companion
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following configurations:

```env
OPENAI_API_KEY=your_openai_api_key
OPEN_AI_MODEL=gpt-4/gpt-3.5-turbo
LLM_PROVIDER=openai/ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Usage

1. Start the microservices:

```bash
python -m app.run_microservices
```

2. Launch the builder application:

```bash
streamlit run app/builder/builder_app.py
```

3. Interact with the chatbot to create your personalized application

## Architecture

- **Base Service**: All microservices inherit from `MicroserviceBase`
- **Port Management**: Dynamic port allocation and service registration
- **LLM Integration**: Flexible support for different LLM providers
- **Template System**: Dynamic app generation using customizable templates
- **Parameter Management**: Structured service parameter handling

## Development

### Adding a New Service

1. Create a new service directory under `app/microservices/`
2. Implement the service class inheriting from `MicroserviceBase`
3. Define service parameters in `app/langchain/service_params.txt`
4. Update service information in `app/services.toml`

### Service Integration

Each service should implement:
- `__init__`: Service initialization and registration
- `register_routes`: API endpoint definitions
- `process_request`: Request handling logic

## Demo Video
![YouTube](https://youtu.be/t5iSYytZdw4)
