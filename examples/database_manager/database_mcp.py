#!/usr/bin/env python3
"""
Database Manager MCP Server

A comprehensive MCP server for database operations.
"""

import asyncio
import sqlite3
from typing import Dict, Any

class DatabaseMCPServer:
    """Database Manager MCP Server"""
    
    def __init__(self):
        self.connections = {}
        
    async def connect_database(self, database_type: str, connection_string: str) -> Dict[str, Any]:
        """Connect to a database"""
        try:
            if database_type == "sqlite":
                conn = sqlite3.connect(connection_string)
                conn.row_factory = sqlite3.Row
                self.connections["default"] = {"type": "sqlite", "connection": conn}
                
                return {
                    "success": True,
                    "message": f"Connected to {database_type} database",
                    "database_type": database_type
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a SQL query"""
        try:
            if "default" not in self.connections:
                return {"success": False, "error": "No database connection"}
            
            conn = self.connections["default"]["connection"]
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.lower().strip().startswith("select"):
                rows = cursor.fetchmany(limit)
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                
                return {
                    "success": True,
                    "data": results,
                    "row_count": len(results)
                }
            else:
                conn.commit()
                return {
                    "success": True,
                    "message": "Query executed successfully",
                    "rows_affected": cursor.rowcount
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

async def main():
    """Demo the database MCP server"""
    db_server = DatabaseMCPServer()
    
    print("🗄️  Database Manager MCP Server Demo")
    print("=" * 40)
    
    # Connect to demo database
    result = await db_server.connect_database("sqlite", "demo.db")
    print(f"Connection: {result}")
    
    # Create demo table
    create_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    """
    result = await db_server.execute_query(create_query)
    print(f"Create table: {result}")
    
    # Insert data
    insert_query = "INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')"
    result = await db_server.execute_query(insert_query)
    print(f"Insert: {result}")
    
    # Query data
    select_query = "SELECT * FROM users"
    result = await db_server.execute_query(select_query)
    print(f"Query results: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 