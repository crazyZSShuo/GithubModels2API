# OpenAI-Compatible API Proxy for GitHub Models

This script provides a lightweight FastAPI server that acts as a proxy between an OpenAI-compatible client and the GitHub Models API (`https://models.github.ai/inference`).

It allows you to use tools and libraries designed for the OpenAI API (like `openai-python`) to interact with GitHub's models by simply changing the base URL.

## Features

- **OpenAI API Compatibility:** Exposes a `/v1/chat/completions` endpoint that mirrors the official OpenAI Chat Completions API.
- **Authentication Forwarding:** Securely passes your `Authorization` header (containing your token) to the upstream GitHub API.
- **Streaming Support:** Fully supports streaming responses (`stream: true`) for real-time interactions.
- **Easy to Run:** Can be started with a single command.

## How It Works

1.  You send a standard OpenAI chat completion request to this server.
2.  The server receives the request, validates the payload, and extracts your `Authorization` header.
3.  It constructs a new request with the same payload and forwards it to `https://models.github.ai/inference/chat/completions`.
4.  It streams the response from the GitHub API directly back to your client.

## Prerequisites

You need Python 3 and the following libraries:
- `fastapi`
- `uvicorn`
- `httpx`

## Installation

1.  Clone or download the `openai_api.py` script.
2.  Install the required dependencies. It's recommended to use a virtual environment.

    ```bash
    pip install fastapi uvicorn httpx
    ```

## Running the Server

To start the server, run the following command in your terminal:

```bash
python openai_api.py
```

The server will start on `http://0.0.0.0:61024`.

## Usage Example

You can interact with the server using any OpenAI-compatible client library or a simple `curl` command.

**Make sure to replace `YOUR_GITHUB_TOKEN` with your actual GitHub token.**

### Non-Streaming Example

```bash
curl http://127.0.0.1:61024/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Hello, who are you?"
      }
    ]
  }'
```

### Streaming Example

```bash
curl http://127.0.0.1:61024/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "user",
        "content": "Write a short story about a robot."
      }
    ],
    "stream": true
  }'
```
