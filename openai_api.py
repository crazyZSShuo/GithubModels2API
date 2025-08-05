import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any

# --- Pydantic Models for OpenAI Compatibility ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = 32768

# --- FastAPI Application ---
app = FastAPI()

# --- Upstream API Configuration ---
UPSTREAM_BASE_URL = "https://models.github.ai/inference"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, http_request: Request):
    """
    Forwards chat completion requests to the upstream OpenAI-compatible API.
    """
    auth_header = http_request.headers.get("Authorization")
    if not auth_header:
        return Response(content="Authorization header is missing", status_code=401)

    url = f"{UPSTREAM_BASE_URL}/chat/completions"

    # Construct the request payload for the upstream API
    payload = {
        "model": request.model,
        "messages": [msg.model_dump() for msg in request.messages],
        "temperature": request.temperature,
        "top_p": request.top_p,
        "n": request.n,
        "stream": request.stream,
        "stop": request.stop,
        "max_tokens": request.max_tokens,
    }

    # Remove None values from the payload
    payload = {k: v for k, v in payload.items() if v is not None}

    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }

    if not request.stream:
        async with httpx.AsyncClient() as client:
            try:
                upstream_response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=300,
                )
                # Return the response from the upstream API directly to the client
                return Response(
                    content=upstream_response.content,
                    status_code=upstream_response.status_code,
                    headers=dict(upstream_response.headers),
                )
            except httpx.RequestError as e:
                return Response(
                    content=f"Error connecting to upstream API: {e}",
                    status_code=500,
                )

    # Handle streaming request
    client = httpx.AsyncClient()
    try:
        upstream_request = client.build_request(
            "POST", url, json=payload, headers=headers, timeout=300
        )
        upstream_response = await client.send(upstream_request, stream=True)

        async def stream_generator():
            try:
                async for chunk in upstream_response.aiter_bytes():
                    yield chunk
            finally:
                await upstream_response.aclose()
                await client.aclose()

        return StreamingResponse(
            stream_generator(),
            status_code=upstream_response.status_code,
            headers=dict(upstream_response.headers),
        )
    except httpx.RequestError as e:
        await client.aclose()
        return Response(
            content=f"Error connecting to upstream API: {e}",
            status_code=500,
        )
    except Exception:
        await client.aclose()
        raise

if __name__ == "__main__":
    import uvicorn
    print("Starting OpenAI compatible API server on http://0.0.0.0:61024")
    uvicorn.run(app, host="0.0.0.0", port=61024)
