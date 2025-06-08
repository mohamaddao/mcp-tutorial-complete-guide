#!/usr/bin/env python3
"""
File Processor MCP Server

A comprehensive MCP server for file processing operations including:
- Reading and writing various file formats
- Text processing and transformation
- File organization and management
- Batch processing operations
"""

import asyncio
import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import mimetypes

class FileProcessorMCPServer:
    """File Processor MCP Server for file operations"""
    
    def __init__(self, base_directory: str = "."):
        self.base_dir = Path(base_directory).resolve()
        self.allowed_extensions = {
            '.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css'
        }
        
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Read a file and return its contents"""
        try:
            full_path = self.base_dir / file_path
            
            # Security check - ensure path is within base directory
            if not str(full_path.resolve()).startswith(str(self.base_dir)):
                return {
                    "success": False,
                    "error": "Access denied: Path outside allowed directory"
                }
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }
            
            # Check file extension
            if full_path.suffix.lower() not in self.allowed_extensions:
                return {
                    "success": False,
                    "error": f"File type not allowed: {full_path.suffix}"
                }
            
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Get file metadata
            stat = full_path.stat()
            
            return {
                "success": True,
                "content": content,
                "file_info": {
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "encoding": encoding,
                    "lines": len(content.splitlines())
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}"
            }
    
    async def write_file(self, file_path: str, content: str, 
                        encoding: str = "utf-8", mode: str = "w") -> Dict[str, Any]:
        """Write content to a file"""
        try:
            full_path = self.base_dir / file_path
            
            # Security check
            if not str(full_path.resolve()).startswith(str(self.base_dir)):
                return {
                    "success": False,
                    "error": "Access denied: Path outside allowed directory"
                }
            
            # Check file extension
            if full_path.suffix.lower() not in self.allowed_extensions:
                return {
                    "success": False,
                    "error": f"File type not allowed: {full_path.suffix}"
                }
            
            # Create directory if it doesn't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, mode, encoding=encoding) as f:
                f.write(content)
            
            # Get file info after writing
            stat = full_path.stat()
            
            return {
                "success": True,
                "message": f"Successfully wrote to {file_path}",
                "file_info": {
                    "path": str(file_path),
                    "size": stat.st_size,
                    "lines": len(content.splitlines()),
                    "mode": mode
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}"
            }
    
    async def list_files(self, directory: str = ".", pattern: str = "*") -> Dict[str, Any]:
        """List files in a directory with optional pattern matching"""
        try:
            dir_path = self.base_dir / directory
            
            # Security check
            if not str(dir_path.resolve()).startswith(str(self.base_dir)):
                return {
                    "success": False,
                    "error": "Access denied: Path outside allowed directory"
                }
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {directory}"
                }
            
            files = []
            for item in dir_path.glob(pattern):
                if item.is_file() and item.suffix.lower() in self.allowed_extensions:
                    stat = item.stat()
                    files.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.base_dir)),
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "type": item.suffix.lower()
                    })
            
            return {
                "success": True,
                "files": sorted(files, key=lambda x: x["name"]),
                "count": len(files),
                "directory": directory
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }
    
    async def process_csv(self, file_path: str, operation: str, **kwargs) -> Dict[str, Any]:
        """Process CSV files with various operations"""
        try:
            full_path = self.base_dir / file_path
            
            if not full_path.exists() or full_path.suffix.lower() != '.csv':
                return {
                    "success": False,
                    "error": "CSV file not found or invalid format"
                }
            
            with open(full_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if operation == "summary":
                return {
                    "success": True,
                    "summary": {
                        "total_rows": len(rows),
                        "columns": list(rows[0].keys()) if rows else [],
                        "sample_data": rows[:3] if rows else []
                    }
                }
            
            elif operation == "filter":
                column = kwargs.get("column")
                value = kwargs.get("value")
                if column and value:
                    filtered = [row for row in rows if row.get(column) == value]
                    return {
                        "success": True,
                        "filtered_data": filtered,
                        "original_count": len(rows),
                        "filtered_count": len(filtered)
                    }
            
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CSV processing failed: {str(e)}"
            }
    
    async def text_analysis(self, file_path: str) -> Dict[str, Any]:
        """Analyze text file for basic statistics"""
        try:
            result = await self.read_file(file_path)
            
            if not result["success"]:
                return result
            
            content = result["content"]
            lines = content.splitlines()
            words = content.split()
            
            # Character frequency
            char_freq = {}
            for char in content.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # Word frequency (top 10)
            word_freq = {}
            for word in words:
                clean_word = ''.join(c for c in word.lower() if c.isalpha())
                if clean_word and len(clean_word) > 2:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "analysis": {
                    "characters": len(content),
                    "lines": len(lines),
                    "words": len(words),
                    "unique_words": len(word_freq),
                    "avg_words_per_line": len(words) / max(len(lines), 1),
                    "top_words": top_words,
                    "file_path": file_path
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text analysis failed: {str(e)}"
            }

async def main():
    """Demo the file processor MCP server"""
    processor = FileProcessorMCPServer()
    
    print("📁 File Processor MCP Server Demo")
    print("=" * 40)
    
    # Create a demo text file
    demo_content = """Hello World!
    This is a demo file for the MCP file processor.
    It contains multiple lines of text for testing.
    We can analyze this text and perform various operations.
    """
    
    # Write demo file
    result = await processor.write_file("demo.txt", demo_content)
    print(f"Write file: {result}")
    
    # Read the file back
    result = await processor.read_file("demo.txt")
    print(f"Read file: {result['success']}")
    if result["success"]:
        print(f"Content preview: {result['content'][:50]}...")
    
    # List files
    result = await processor.list_files(".", "*.txt")
    print(f"List files: {result}")
    
    # Analyze text
    result = await processor.text_analysis("demo.txt")
    print(f"Text analysis: {result}")
    
    # Create and process CSV
    csv_content = """name,age,city
Alice,25,New York
Bob,30,London
Carol,28,Paris
David,35,Tokyo
"""
    
    result = await processor.write_file("demo.csv", csv_content)
    print(f"CSV write: {result['success']}")
    
    result = await processor.process_csv("demo.csv", "summary")
    print(f"CSV summary: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 