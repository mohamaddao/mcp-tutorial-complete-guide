# 🗄️ Database Manager MCP Example

A comprehensive MCP server for database operations supporting multiple database types with safe query execution and CRUD operations.

## 🎯 Features

- **Multi-Database Support**: SQLite, PostgreSQL, MongoDB
- **Safe Query Execution**: Protection against destructive operations
- **CRUD Operations**: Create, Read, Update, Delete with validation
- **Schema Management**: Table listing and description tools
- **Connection Management**: Multiple named database connections

## 🚀 Quick Start

```bash
# Navigate to database manager
cd examples/database_manager

# Install dependencies
pip install sqlite3 sqlalchemy pandas psycopg2-binary

# Run the demo
python database_mcp.py
```

## 🔧 Available Tools

### 1. `connect_database`
Connect to a database with named connections.

### 2. `execute_query` 
Execute SQL queries with safety checks.

### 3. `list_tables`
Get all tables in the database.

### 4. `describe_table`
Get table schema and column information.

### 5. `insert_data`
Safely insert data into tables.

## 🛡️ Safety Features

- Prevents destructive operations (DROP, DELETE, TRUNCATE)
- Input validation and sanitization
- Connection pooling and management
- Query result limiting

## 🎓 Learning Objectives

This example demonstrates:
- Multi-database MCP architecture
- Safe database operation patterns
- Error handling for database operations
- Connection management strategies 