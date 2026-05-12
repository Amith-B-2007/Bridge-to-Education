"""
Shared Ollama HTTP client. Use this in every module that needs to call llama3.

Why a shared file?
- Every team member's module (Study Hub, AI Tutor, Schemes RAG, Career Guidance)
  will need to talk to Ollama. Putting one wrapper here means:
    - One place to change the model name
    - One place to handle errors
    - Easy to mock for tests

Run Ollama locally first:
    ollama serve              # starts the server on port 11434
    ollama pull llama3        # downloads the model
"""
import os
import json
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def chat(messages, system_prompt=None, stream=False, temperature=0.7):
    """
    Send a chat request to Ollama and return the response.

    Args:
        messages: list of {"role": "user"|"assistant", "content": "..."}
        system_prompt: optional system message that sets the AI's role
        stream: if True, returns a generator that yields text chunks
                if False, returns the full reply as a string
        temperature: 0.0 = deterministic, 1.0 = creative. 0.7 is a good default.

    Returns:
        If stream=False: a string (the full reply)
        If stream=True: a generator yielding strings (text chunks)

    Example:
        reply = chat([{"role": "user", "content": "Hi"}], system_prompt="Be brief.")
        print(reply)
    """
    payload_messages = []
    if system_prompt:
        payload_messages.append({"role": "system", "content": system_prompt})
    payload_messages.extend(messages)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": payload_messages,
        "stream": stream,
        "options": {"temperature": temperature},
    }

    if stream:
        return _stream_chat(payload)
    return _full_chat(payload)


def _full_chat(payload):
    """Non-streaming: send request, wait for full reply."""
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        return (
            "[AI service unavailable] Please make sure Ollama is running.\n"
            "Run `ollama serve` in a terminal, then `ollama pull llama3`."
        )
    except Exception as e:
        return f"[AI error] {e}"


def _stream_chat(payload):
    """Streaming generator: yields text chunks as they arrive."""
    try:
        with requests.post(
            f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=120
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.ConnectionError:
        yield "[AI service unavailable] Please run `ollama serve`."
    except Exception as e:
        yield f"[AI error] {e}"


def is_available():
    """Quick health check. Returns True if Ollama is reachable."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False
