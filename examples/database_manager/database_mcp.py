#!/usr/bin/env python3
"""
Database MCP Server

A comprehensive MCP server for database operations using FastMCP.
Demonstrates:
- SQL query execution
- Database connection management
- Type-safe operations
- Resource providers
"""

import asyncio
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import BaseModel

# Initialize FastMCP server
mcp = FastMCP("database_tools")

class QueryResult(BaseModel):
    """Model for query results"""
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time: float

class DatabaseConfig(BaseModel):
    """Database configuration model"""
    type: str
    connection_string: str
    max_connections: int = 10

# System prompts
@mcp.prompt()
def system_prompt() -> str:
    """Define the database assistant's role"""
    return """
    You are a database assistant that helps users interact with databases safely.
    Always validate queries before execution and use proper error handling.
    Never execute dangerous operations without confirmation.
    """

@mcp.prompt()
def error_prompt() -> str:
    """Handle database errors"""
    return """
    I encountered an error while working with the database.
    This could be due to:
    - Invalid SQL syntax
    - Connection issues
    - Permission problems
    - Resource constraints
    Please check your query and try again.
    """

# Database resources
@mcp.resource("db://{database}/{table}")
async def get_table_info(database: str, table: str) -> Dict:
    """Get metadata about a database table"""
    try:
        conn = sqlite3.connect(f"{database}.db")
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        return {
            "table": table,
            "columns": [col[1] for col in columns],
            "types": [col[2] for col in columns],
            "last_checked": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# Database tools
@mcp.tool()
async def execute_query(query: str, limit: int = 100) -> Dict:
    """
    Execute a SQL query safely
    
    Args:
        query: SQL query to execute
        limit: Maximum number of rows to return
        
    Returns:
        Dictionary with query results or error information
    """
    try:
        # In production, use connection pooling
        conn = sqlite3.connect("demo.db")
        cursor = conn.cursor()
        
        start_time = datetime.now()
        cursor.execute(query)
        
        if query.lower().strip().startswith("select"):
            rows = cursor.fetchmany(limit)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "data": QueryResult(
                    columns=columns,
                    rows=results,
                    row_count=len(results),
                    execution_time=execution_time
                ).dict()
            }
        else:
            conn.commit()
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "data": {
                    "rows_affected": cursor.rowcount,
                    "execution_time": execution_time
                }
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def get_table_schema(table: str) -> Dict:
    """
    Get schema information for a table
    
    Args:
        table: Name of the table
        
    Returns:
        Dictionary with table schema information
    """
    try:
        # Get schema from resource
        schema = await get_table_info("demo", table)
        
        if "error" in schema:
            raise Exception(schema["error"])
            
        return {
            "success": True,
            "data": schema
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def validate_query(query: str) -> Dict:
    """
    Validate a SQL query without executing it
    
    Args:
        query: SQL query to validate
        
    Returns:
        Dictionary with validation results
    """
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        # SQLite will parse but not execute in prepare mode
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
        
        return {
            "success": True,
            "data": {
                "is_valid": True,
                "query_plan": plan,
                "validation_time": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "is_valid": False,
                "validation_time": datetime.now().isoformat()
            }
        }

if __name__ == "__main__":
    # Run the MCP server
    print("🗄️  Starting Database MCP Server...")
    mcp.run(transport="streamable-http") 