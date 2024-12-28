from gradio_client import Client
import os

HF_TOKEN = os.environ.get("HF_TOKEN")

client = Client("bassamadnan/qwen", hf_token=HF_TOKEN)
result = client.predict(
		input_text="Hello!!",
		api_name="/predict"
)
print(result)