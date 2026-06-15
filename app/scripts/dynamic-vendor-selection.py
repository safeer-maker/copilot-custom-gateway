from fastapi import FastAPI, Depends
# from .auth import verify_api_key
from pydantic import BaseModel

app = FastAPI()

@app.get("/v1/models")
async def list_models(_token: str):
    """
    Exposes available endpoints to the VS Code client model picker interface.
    This endpoint is invoked automatically by VS Code to populate the model list.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "qwen3.6-coder-7b",
                "object": "model",
                "created": 1718471152,
                "owned_by": "private-infrastructure"
            },
            {
                "id": "deepseek-coder-v2",
                "object": "model",
                "created": 1718471152,
                "owned_by": "private-infrastructure"
            }
        ]
        # "data": [
        #     {
        #         "id": "qwen3.6-coder-7b",
        #         "object": "model",
        #         "created": 1718471152,
        #         "owned_by": "private-infrastructure",
        #         "tool_calling": True,  # Enables Copilot Agent view actions
        #         "context_window": 128000
        #     },
        #     {
        #         "id": "deepseek-coder-v2",
        #         "object": "model",
        #         "created": 1718471152,
        #         "owned_by": "private-infrastructure",
        #         "tool_calling": True,
        #         "context_window": 64048
        #     },
        #     {
        #         "id": "llama3-70b-instruct",
        #         "object": "model",
        #         "created": 1718471152,
        #         "owned_by": "private-infrastructure",
        #         "tool_calling": False, # Basic chat view support only
        #         "context_window": 8192
        #     }
        # ]
    }

@app.get("/api/tags")
async def list_ollama_models():
    """
    Emulates Ollama's model tag discovery. 
    VS Code will read this and auto-populate the picker dropdown.
    """
    return {
        "models": [
            {
                "name": "qwen3.6-coder-7b:latest",
                "model": "qwen3.6-coder-7b:latest",
                "modified_at": "2026-06-15T11:46:00Z",
                "size": 4700000000,
                "digest": "sha256:qwen7bcache",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "qwen2",
                    "families": ["qwen2"],
                    "parameter_size": "7B",
                    "quantization_level": "Q4_K_M"
                }
            },
            {
                "name": "deepseek-coder-v2:latest",
                "model": "deepseek-coder-v2:latest",
                "modified_at": "2026-06-15T11:46:00Z",
                "size": 8900000000,
                "digest": "sha256:deepseekv2cache",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": "16B",
                    "quantization_level": "Q4_K_M"
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)