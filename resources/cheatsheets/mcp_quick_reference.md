# 🚀 FastMCP Quick Reference

## 📋 Core Components

| Component | Description | Example |
|-----------|-------------|---------|
| **FastMCP** | Modern MCP framework | `mcp = FastMCP("my_server")` |
| **Tools** | Decorated functions | `@mcp.tool()` |
| **Resources** | Data providers | `@mcp.resource("data://{id}")` |
| **Prompts** | System instructions | `@mcp.prompt()` |
| **Models** | Type definitions | `class DataModel(BaseModel)` |

## 🔧 Modern Server Structure

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import Dict, Optional

# Initialize server
mcp = FastMCP("my_server")

# Define models
class ResponseData(BaseModel):
    value: str
    timestamp: datetime
    metadata: Optional[Dict]

# Define prompts
@mcp.prompt()
def system_prompt() -> str:
    return """System instructions..."""

# Define resources
@mcp.resource("data://{id}")
async def get_data(id: str) -> Dict:
    """Get data by ID"""
    return {"id": id, "value": "data"}

# Define tools
@mcp.tool()
async def process_data(input: str) -> Dict:
    """Process input data"""
    try:
        result = ResponseData(
            value=input,
            timestamp=datetime.now()
        )
        return {
            "success": True,
            "data": result.dict()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

# Run server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## 📨 Type-Safe Responses

```python
# Success Response
{
    "success": True,
    "data": {
        "value": "processed",
        "timestamp": "2025-06-08T10:30:00",
        "metadata": {
            "source": "tool"
        }
    }
}

# Error Response
{
    "success": False,
    "error": "Invalid input",
    "prompt": "error_prompt"
}
```

## 🛠️ Common Patterns

### 1. Resource Provider
```python
@mcp.resource("file://{path}")
async def get_file_info(path: str) -> FileInfo:
    """Get file metadata"""
    stat = Path(path).stat()
    return FileInfo(
        path=path,
        size=stat.st_size,
        modified=stat.st_mtime
    )
```

### 2. API Integration
```python
@mcp.tool()
async def call_api(endpoint: str) -> Dict:
    """Call external API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/{endpoint}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        data = response.json()
        return {
            "success": True,
            "data": APIResponse(**data).dict()
        }
```

### 3. Database Operations
```python
@mcp.tool()
async def query_db(sql: str) -> Dict:
    """Execute database query"""
    async with db_pool.acquire() as conn:
        result = await conn.fetch(sql)
        return {
            "success": True,
            "data": QueryResult(rows=result).dict()
        }
```

## 🔐 Best Practices

### ✅ Do
- Use type hints everywhere
- Define Pydantic models
- Implement resource providers
- Use system prompts
- Handle errors gracefully
- Document with docstrings

### ❌ Don't
- Skip type validation
- Return raw data
- Ignore error handling
- Mix business logic
- Hardcode configurations

## 🚀 Development Workflow

1. **Setup**
```bash
pip install mcp langchain-core pydantic
```

2. **Structure**
```
my_server/
├── models.py      # Pydantic models
├── prompts.py     # System prompts
├── resources.py   # Resource providers
├── tools.py       # MCP tools
└── server.py      # FastMCP setup
```

3. **Testing**
```python
from mcp.testing import MCPTestClient

async def test_tool():
    client = MCPTestClient(your_mcp)
    result = await client.call_tool("my_tool", {"param": "value"})
    assert result.success == True
```

## 🔍 Debugging Tips

| Issue | Solution |
|-------|----------|
| Type error | Check Pydantic models |
| Resource 404 | Verify resource path |
| Tool error | Check error prompt |
| Performance | Use async/await |
| Memory leak | Close connections |

## 📚 Learning Resources

- 📖 [FastMCP Documentation](https://mcp.dev/fastmcp)
- 🎓 [Interactive Tutorials](../notebooks/)
- 💡 [Example Projects](../examples/)
- 🛠️ [Templates](../templates/)

---

**💡 Pro Tip**: Use FastMCP's type system to catch errors at compile time rather than runtime! 