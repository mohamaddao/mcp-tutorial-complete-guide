#!/usr/bin/env python3
"""
File Processor MCP Server

A comprehensive MCP server for file operations using FastMCP.
Demonstrates:
- Secure file handling
- Resource providers
- Type validation
- Error handling
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import mimetypes

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import BaseModel

# Initialize FastMCP server
mcp = FastMCP("file_tools")

class FileInfo(BaseModel):
    """File information model"""
    path: str
    size: int
    modified: float
    mime_type: str
    hash: Optional[str]

class FileContent(BaseModel):
    """File content model"""
    content: str
    encoding: str
    lines: int
    info: FileInfo

class TextAnalysis(BaseModel):
    """Text analysis results model"""
    characters: int
    words: int
    lines: int
    unique_words: int
    top_words: List[tuple]
    file_info: FileInfo

# System prompts
@mcp.prompt()
def system_prompt() -> str:
    """Define the file processor's role"""
    return """
    You are a file processing assistant that helps users work with files safely.
    Always validate paths and file operations before execution.
    Never perform dangerous operations without confirmation.
    """

@mcp.prompt()
def error_prompt() -> str:
    """Handle file operation errors"""
    return """
    I encountered an error while processing the file.
    This could be due to:
    - Invalid file path
    - Permission issues
    - File not found
    - Unsupported file type
    Please check the file and try again.
    """

# File resources
@mcp.resource("file://{path}")
async def get_file_info(path: str) -> Dict:
    """Get metadata about a file"""
    try:
        full_path = Path(path).resolve()
        
        if not full_path.exists():
            return {"error": "File not found"}
            
        stat = full_path.stat()
        mime_type, _ = mimetypes.guess_type(str(full_path))
        
        # Calculate file hash
        sha256_hash = hashlib.sha256()
        with open(full_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return FileInfo(
            path=str(full_path),
            size=stat.st_size,
            modified=stat.st_mtime,
            mime_type=mime_type or "application/octet-stream",
            hash=sha256_hash.hexdigest()
        ).dict()
        
    except Exception as e:
        return {"error": str(e)}

# File operation tools
@mcp.tool()
async def read_file(file_path: str, encoding: str = "utf-8") -> Dict:
    """
    Read a file safely
    
    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        
    Returns:
        Dictionary with file contents and metadata
    """
    try:
        # Get file info from resource
        file_info = await get_file_info(file_path)
        
        if "error" in file_info:
            raise Exception(file_info["error"])
            
        # Validate file type
        if not file_info["mime_type"].startswith(("text/", "application/")):
            raise Exception("Unsupported file type")
            
        # Read file
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
            
        return {
            "success": True,
            "data": FileContent(
                content=content,
                encoding=encoding,
                lines=len(content.splitlines()),
                info=FileInfo(**file_info)
            ).dict()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def write_file(file_path: str, content: str, encoding: str = "utf-8") -> Dict:
    """
    Write content to a file safely
    
    Args:
        file_path: Path to write to
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        Dictionary with operation results
    """
    try:
        # Validate path
        full_path = Path(file_path).resolve()
        
        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, "w", encoding=encoding) as f:
            f.write(content)
            
        # Get updated file info
        file_info = await get_file_info(str(full_path))
        
        return {
            "success": True,
            "data": {
                "path": str(full_path),
                "size": file_info["size"],
                "lines": len(content.splitlines()),
                "encoding": encoding
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def analyze_text(file_path: str) -> Dict:
    """
    Analyze text file contents
    
    Args:
        file_path: Path to text file
        
    Returns:
        Dictionary with text analysis results
    """
    try:
        # Read file first
        result = await read_file(file_path)
        
        if not result["success"]:
            raise Exception(result["error"])
            
        content = result["data"]["content"]
        file_info = FileInfo(**result["data"]["info"])
        
        # Analyze content
        words = content.split()
        word_freq = {}
        
        for word in words:
            clean_word = "".join(c.lower() for c in word if c.isalpha())
            if clean_word and len(clean_word) > 2:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
                
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "success": True,
            "data": TextAnalysis(
                characters=len(content),
                words=len(words),
                lines=len(content.splitlines()),
                unique_words=len(word_freq),
                top_words=top_words,
                file_info=file_info
            ).dict()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def process_csv(file_path: str, operation: str = "summary", **kwargs) -> Dict:
    """
    Process CSV files with various operations
    
    Args:
        file_path: Path to CSV file
        operation: Operation to perform (summary, filter)
        **kwargs: Additional operation parameters
        
    Returns:
        Dictionary with operation results
    """
    try:
        # Validate file type
        file_info = await get_file_info(file_path)
        
        if "error" in file_info:
            raise Exception(file_info["error"])
            
        if not file_info["mime_type"] in ["text/csv", "application/csv"]:
            raise Exception("Not a CSV file")
            
        # Read CSV
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if operation == "summary":
            return {
                "success": True,
                "data": {
                    "total_rows": len(rows),
                    "columns": list(rows[0].keys()) if rows else [],
                    "sample": rows[:3] if rows else [],
                    "file_info": file_info
                }
            }
            
        elif operation == "filter":
            column = kwargs.get("column")
            value = kwargs.get("value")
            
            if not (column and value):
                raise Exception("Filter requires column and value")
                
            filtered = [row for row in rows if row.get(column) == value]
            
            return {
                "success": True,
                "data": {
                    "filtered_rows": filtered,
                    "total_matches": len(filtered),
                    "filter_info": {"column": column, "value": value},
                    "file_info": file_info
                }
            }
            
        else:
            raise Exception(f"Unknown operation: {operation}")
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

if __name__ == "__main__":
    # Run the MCP server
    print("📁 Starting File Processor MCP Server...")
    mcp.run(transport="streamable-http") 