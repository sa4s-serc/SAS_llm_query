from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from gradio_client import Client
import os

class CodeQwenLLM(LLM):
    """Custom LLM class for CodeQwen"""
    
    # Define class variables
    hf_token: Optional[str] = None
    client: Optional[Client] = None
    
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hf_token = os.environ.get("HF_TOKEN")
        self.client = Client("bassamadnan/qwen", hf_token=self.hf_token)
        
    @property
    def _llm_type(self) -> str:
        return "code_qwen"
        
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the LLM call."""
        if self.client is None:
            raise ValueError("Client not initialized")
        response = self.client.predict(
            input_text=prompt,
            api_name="/predict"
        )
        return response

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": "CodeQwen1.5-7B-Chat"
        }