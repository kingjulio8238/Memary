"""Anonymous Parallel Search MCP over Streamable HTTP (Python 3.8 compatible)."""

import json
import math
import uuid
from urllib.parse import urlsplit

import requests


ENDPOINT = "https://search.parallel.ai/mcp"
USER_AGENT = "Memary/0.1.2 (+https://github.com/kingjulio8238/Memary)"
PROTOCOL_VERSION = "2025-03-26"
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class ParallelSearch:
    """Search excerpts, or fetch a standalone HTTP(S) URL, without credentials.

    Each call opens an MCP session; the conversation identifier remains stable.
    HTTP errors, tool errors and interruptions propagate without provider fallback.
    ``timeout`` bounds each HTTP connection/read, including initialization.
    """

    def __init__(self, timeout=30.0):
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("search_timeout must be a positive finite number")
        self.timeout = timeout
        self.session_id = str(uuid.uuid4())

    def search(self, query: str) -> str:
        query = query.strip()
        if not query:
            raise ValueError("Search query must not be empty")
        url = urlsplit(query)
        if url.scheme in ("http", "https") and url.netloc and not any(
            character.isspace() for character in query
        ):
            name, arguments = "web_fetch", {"urls": [query]}
        else:
            name, arguments = "web_search", {
                "objective": query,
                "search_queries": [query],
            }
        arguments["session_id"] = self.session_id
        with requests.Session() as session:
            # Never attach ambient .netrc credentials to the anonymous endpoint.
            # Keep proxy/CA environment settings available through requests.
            session.auth = _AnonymousAuth()
            session.headers.update({
                "User-Agent": USER_AGENT,
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            })
            initialized = self._post(session, "initialize", {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "memary", "version": "0.1.2"},
            }, 1)
            if initialized.get("protocolVersion") != PROTOCOL_VERSION:
                raise RuntimeError("Parallel MCP negotiated an unsupported protocol")
            session.headers["MCP-Protocol-Version"] = PROTOCOL_VERSION
            self._post(session, "notifications/initialized", {}, None)
            result = self._post(session, "tools/call", {
                "name": name, "arguments": arguments,
            }, 2)
        text = "\n".join(
            item["text"] for item in result.get("content", [])
            if item.get("type") == "text" and isinstance(item.get("text"), str)
        )
        if result.get("isError"):
            raise RuntimeError("Parallel MCP tool error: " + text)
        if not text:
            raise RuntimeError("Parallel MCP returned no text content")
        return text

    def _post(self, session, method, params, request_id):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            message["id"] = request_id
        with session.post(
            ENDPOINT, json=message, timeout=self.timeout,
            stream=True, allow_redirects=False,
        ) as response:
            response.raise_for_status()
            if response.is_redirect:
                raise RuntimeError("Unexpected Parallel MCP redirect")
            if method == "initialize" and response.headers.get("Mcp-Session-Id"):
                session.headers["Mcp-Session-Id"] = response.headers["Mcp-Session-Id"]
            if request_id is None:
                return {}
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type == "text/event-stream":
                return self._read_events(response, request_id)
            if content_type != "application/json":
                raise RuntimeError("Unexpected Parallel MCP response content type")
            chunks, size = [], 0
            for chunk in response.iter_content(chunk_size=65536):
                size += len(chunk)
                if size > MAX_RESPONSE_BYTES:
                    raise RuntimeError("Parallel MCP response is too large")
                chunks.append(chunk)
            return self._result(json.loads(b"".join(chunks)), request_id)

    def _read_events(self, response, request_id):
        data, size = [], 0
        for line in response.iter_lines():
            size += len(line) + 1
            if size > MAX_RESPONSE_BYTES:
                raise RuntimeError("Parallel MCP response is too large")
            if line.startswith(b"data:"):
                data.append(line[5:].lstrip(b" ").decode("utf-8"))
            elif not line and data:
                message = json.loads("\n".join(data))
                data = []
                if message.get("id") == request_id:
                    return self._result(message, request_id)
        raise RuntimeError("Parallel MCP stream ended without a response")

    @staticmethod
    def _result(message, request_id):
        if message.get("jsonrpc") != "2.0" or message.get("id") != request_id:
            raise RuntimeError("Invalid Parallel MCP response")
        if "error" in message:
            raise RuntimeError("Parallel MCP error: " + str(message["error"]))
        if not isinstance(message.get("result"), dict):
            raise RuntimeError("Parallel MCP response has no result")
        return message["result"]


class _AnonymousAuth(requests.auth.AuthBase):
    def __call__(self, request):
        request.headers.pop("Authorization", None)
        return request
