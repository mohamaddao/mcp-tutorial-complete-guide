#!/usr/bin/env python3
"""
Basic MCP Server Template

Use this template as a starting point for your own MCP servers.
Replace the example tools with your own functionality.

Usage:
    python basic_mcp_server.py

Requirements:
    pip install mcp fastapi uvicorn pydantic
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class MCPTool:
    """Represents an MCP tool that can be called"""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: callable

@dataclass
class MCPRequest:
    """Represents a request to an MCP tool"""
    tool_name: str
    arguments: Dict[str, Any]

@dataclass 
class MCPResponse:
    """Represents a response from an MCP tool"""
    success: bool
    result: Any = None
    error: str = None

class BasicMCPServer:
    """
    Template for a basic MCP server.
    
    Customize this class by:
    1. Adding your own tools in __init__
    2. Implementing your tool handler functions
    3. Adding any required initialization
    """
    
    def __init__(self, name: str = "BasicMCPServer"):
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
        
        # Add your tools here
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        
        # Example tool 1: Echo tool
        echo_tool = MCPTool(
            name="echo",
            description="Echo back the input message",
            parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to echo back"
                    }
                },
                "required": ["message"]
            },
            handler=self.echo
        )
        self.add_tool(echo_tool)
        
        # Example tool 2: Math calculator
        calculator_tool = MCPTool(
            name="calculate",
            description="Perform basic mathematical operations",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "Mathematical operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number"
                    }
                },
                "required": ["operation", "a", "b"]
            },
            handler=self.calculate
        )
        self.add_tool(calculator_tool)
        
        # TODO: Add your own tools here
        # Example:
        # your_tool = MCPTool(
        #     name="your_tool_name",
        #     description="Description of what your tool does",
        #     parameters={...},
        #     handler=self.your_handler_function
        # )
        # self.add_tool(your_tool)
    
    def add_tool(self, tool: MCPTool):
        """Register a new tool with the server"""
        self.tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")
    
    def list_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[MCPTool]:
        """Get information about a specific tool"""
        return self.tools.get(tool_name)
    
    async def call_tool(self, request: MCPRequest) -> MCPResponse:
        """Execute a tool and return the response"""
        if request.tool_name not in self.tools:
            return MCPResponse(
                success=False, 
                error=f"Tool '{request.tool_name}' not found"
            )
        
        try:
            tool = self.tools[request.tool_name]
            result = await tool.handler(**request.arguments)
            return MCPResponse(success=True, result=result)
        except Exception as e:
            return MCPResponse(
                success=False, 
                error=f"Tool execution failed: {str(e)}"
            )
    
    # Example tool implementations
    async def echo(self, message: str) -> str:
        """Echo back the input message"""
        return f"Echo: {message}"
    
    async def calculate(self, operation: str, a: float, b: float) -> Dict[str, Any]:
        """Perform basic mathematical operations"""
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else None
        }
        
        if operation == "divide" and b == 0:
            raise ValueError("Cannot divide by zero")
        
        result = operations[operation]
        return {
            "operation": operation,
            "inputs": {"a": a, "b": b},
            "result": result
        }
    
    # TODO: Add your own tool handler functions here
    # async def your_handler_function(self, param1: str, param2: int) -> Any:
    #     """Your custom tool implementation"""
    #     # Implement your tool logic here
    #     return {"your": "result"}

async def main():
    """Demo and test the MCP server"""
    # Create your server
    server = BasicMCPServer("MyCustomMCPServer")
    
    print(f"🚀 Starting {server.name}")
    print(f"📋 Available tools: {server.list_tools()}")
    print()
    
    # Test the tools
    test_requests = [
        MCPRequest("echo", {"message": "Hello, MCP!"}),
        MCPRequest("calculate", {"operation": "add", "a": 10, "b": 5}),
        MCPRequest("calculate", {"operation": "multiply", "a": 3, "b": 7}),
    ]
    
    for request in test_requests:
        print(f"🔧 Testing tool: {request.tool_name}")
        response = await server.call_tool(request)
        
        if response.success:
            print(f"✅ Success: {response.result}")
        else:
            print(f"❌ Error: {response.error}")
        print()

if __name__ == "__main__":
    asyncio.run(main()) 