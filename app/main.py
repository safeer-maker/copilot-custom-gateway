import json
import os
import time
import uuid
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from pydantic import BaseModel

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

app = FastAPI(title="Copilot Gateway")


# ── Pydantic schemas (OpenAI-compatible) ──────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str | list | None = None
    tool_calls: list | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatRequest(BaseModel):
    model: str = GEMINI_MODEL
    messages: list[Message]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    tools: list | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def to_langchain_messages(messages: list[Message]):
    lc = []
    for m in messages:
        content = m.content or ""
        if isinstance(content, list):
            # multipart content — flatten to text for now
            content = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            )
        if m.role == "system":
            lc.append(SystemMessage(content=content))
        elif m.role == "user":
            lc.append(HumanMessage(content=content))
        elif m.role == "assistant":
            lc.append(AIMessage(content=content))
        elif m.role == "tool":
            lc.append(ToolMessage(content=content, tool_call_id=m.tool_call_id or ""))
    return lc


def openai_response(ai_message: AIMessage, model: str) -> dict:
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ai_message.content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def openai_chunk(delta_content: str, model: str, finish_reason: str | None = None) -> str:
    chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": delta_content},
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {json.dumps(chunk)}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/v1/models")
async def list_models():
    """VSCode calls this to populate the model picker dropdown."""
    return {
        "object": "list",
        "data": [
            {
                "id": GEMINI_MODEL,
                "object": "model",
                "created": 1718471152,
                "owned_by": "copilot-gateway",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    llm = ChatGoogleGenerativeAI(
        model=request.model if request.model else GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=request.temperature if request.temperature is not None else 0.2,
        max_output_tokens=request.max_tokens,
        streaming=request.stream,
    )

    lc_messages = to_langchain_messages(request.messages)

    if request.stream:
        async def sse_generator():
            async for chunk in llm.astream(lc_messages):
                if chunk.content:
                    yield openai_chunk(chunk.content, request.model)
            yield openai_chunk("", request.model, finish_reason="stop")
            yield "data: [DONE]\n\n"

        return StreamingResponse(sse_generator(), media_type="text/event-stream")

    response = await llm.ainvoke(lc_messages)
    return openai_response(response, request.model)
