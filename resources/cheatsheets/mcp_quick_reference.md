# 🚀 MCP Quick Reference Cheat Sheet

## 📋 Core Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **MCP Server** | Provides tools and resources to clients | Weather API, Database connector |
| **MCP Client** | AI assistant that uses tools | Claude, ChatGPT with MCP |
| **Tool** | Function that can be called by client | `get_weather()`, `read_file()` |
| **Resource** | Data source accessible to client | Files, database tables, API endpoints |
| **Transport** | Communication layer | HTTP, WebSocket, Unix socket |

## 🔧 Basic Server Structure

```python
class MCPServer:
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def add_tool(self, tool):
        self.tools[tool.name] = tool
    
    async def call_tool(self, request):
        # Tool execution logic
        pass
```

## 📨 Message Format (JSON-RPC 2.0)

### Tool Call Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "call_tool",
  "params": {
    "tool_name": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "units": "celsius"
    }
  }
}
```

### Tool Call Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "data": {
      "temperature": 22.5,
      "condition": "Partly Cloudy"
    }
  }
}
```

## 🛠️ Tool Definition Schema

```python
tool_definition = {
    "name": "tool_name",
    "description": "What the tool does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            },
            "param2": {
                "type": "number",
                "minimum": 0,
                "description": "Numeric parameter"
            }
        },
        "required": ["param1"]
    }
}
```

## 🔍 Common Parameter Types

| Type | JSON Schema | Example | Description |
|------|-------------|---------|-------------|
| **String** | `"type": "string"` | `"hello"` | Text data |
| **Number** | `"type": "number"` | `42.5` | Integer or float |
| **Boolean** | `"type": "boolean"` | `true` | True/false value |
| **Array** | `"type": "array"` | `[1, 2, 3]` | List of items |
| **Object** | `"type": "object"` | `{"key": "value"}` | Dictionary/map |
| **Enum** | `"enum": ["a", "b"]` | `"a"` | One of specified values |

## 🛡️ Error Handling Patterns

```python
try:
    result = await some_operation()
    return {
        "success": True,
        "data": result
    }
except ValueError as e:
    return {
        "success": False,
        "error": f"Invalid input: {str(e)}"
    }
except Exception as e:
    return {
        "success": False,
        "error": f"Operation failed: {str(e)}"
    }
```

## 🔐 Security Best Practices

### ✅ Do
- Validate all input parameters
- Use allowlists for file paths/operations
- Implement rate limiting
- Log security events
- Use environment variables for secrets

### ❌ Don't
- Execute arbitrary code from user input
- Allow path traversal (`../../../etc/passwd`)
- Store secrets in code
- Trust user input without validation
- Expose internal error details

## 📊 Testing Your MCP Server

```python
async def test_tool():
    server = YourMCPServer()
    
    # Test successful case
    request = MCPRequest(
        tool_name="your_tool",
        arguments={"param": "value"}
    )
    response = await server.call_tool(request)
    assert response.success == True
    
    # Test error case
    bad_request = MCPRequest(
        tool_name="nonexistent_tool",
        arguments={}
    )
    response = await server.call_tool(bad_request)
    assert response.success == False
```

## 🚀 Deployment Commands

```bash
# Development server
python your_mcp_server.py

# Production with Uvicorn
uvicorn your_server:app --host 0.0.0.0 --port 8000

# Docker deployment
docker build -t my-mcp-server .
docker run -p 8000:8000 my-mcp-server

# Kubernetes
kubectl apply -f mcp-deployment.yaml
```

## 🔄 Transport Layer Examples

### HTTP/FastAPI
```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/mcp")
async def handle_mcp(request: MCPRequest):
    return await server.call_tool(request)
```

### WebSocket
```python
import websockets

async def handle_websocket(websocket, path):
    async for message in websocket:
        request = json.loads(message)
        response = await server.call_tool(request)
        await websocket.send(json.dumps(response))
```

## 🎯 Common Tool Patterns

### File Operations
```python
async def read_file(self, path: str) -> Dict:
    if not self._is_safe_path(path):
        raise ValueError("Unsafe path")
    
    with open(path, 'r') as f:
        content = f.read()
    
    return {"content": content, "size": len(content)}
```

### API Integration
```python
async def call_api(self, endpoint: str) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.base_url}/{endpoint}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
```

### Database Query
```python
async def query_db(self, sql: str) -> Dict:
    if not self._is_safe_query(sql):
        raise ValueError("Unsafe query")
    
    async with self.db_pool.acquire() as conn:
        result = await conn.fetch(sql)
        return {"rows": [dict(row) for row in result]}
```

## 📚 Quick Commands

| Task | Command |
|------|---------|
| Install MCP | `pip install mcp` |
| Create server | `cp resources/templates/basic_mcp_server.py my_server.py` |
| Run tests | `pytest tests/` |
| Check format | `black . && flake8 .` |
| Build docs | `sphinx-build docs/ docs/_build/` |

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Tool not found | Check tool registration and spelling |
| Parameter validation error | Verify parameter types and requirements |
| Permission denied | Check file/directory permissions |
| Connection refused | Verify server is running and port is correct |
| Import errors | Check dependencies: `pip install -r requirements.txt` |

## 📞 Getting Help

- 📖 **Documentation**: [notebooks/](../notebooks/)
- 💬 **Community**: GitHub Discussions
- 🐛 **Issues**: GitHub Issues  
- 📧 **Support**: Check the main README

---

**💡 Pro Tip**: Always test your MCP tools with both valid and invalid inputs to ensure robust error handling! 