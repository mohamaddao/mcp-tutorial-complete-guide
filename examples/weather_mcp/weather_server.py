#!/usr/bin/env python3
"""
Weather MCP Server Example

This example demonstrates a complete MCP server that provides weather information
using the official MCP FastMCP implementation.

Usage:
    python weather_server.py

Requirements:
    pip install mcp uvicorn fastapi httpx pydantic langchain-core
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from mcp.server.fastmcp import FastMCP
import mcp.types as types
from pydantic import BaseModel
import httpx

# Initialize FastMCP server
mcp = FastMCP("weather_tools")

class WeatherData(BaseModel):
    """Weather data model"""
    location: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    timestamp: datetime

# System prompt for the weather assistant
@mcp.prompt()
def system_prompt() -> str:
    """Define the AI assistant's role"""
    return """
    You are a weather assistant that provides accurate weather information.
    Use the available tools to fetch current conditions and forecasts.
    Always specify temperature units and provide clear, concise responses.
    """

@mcp.prompt()
def error_prompt() -> str:
    """Handle error cases"""
    return """
    I apologize, but I was unable to fetch the weather data.
    This could be due to:
    - Invalid location name
    - Weather service unavailability
    - Network connectivity issues
    Please try again with a valid city name.
    """

# Resource for cached weather data
@mcp.resource("weather://{location}")
async def get_weather_resource(location: str) -> Dict:
    """Get cached weather data for a location"""
    # In a real implementation, this would check a cache first
    return {
        "location": location,
        "last_updated": datetime.now().isoformat(),
        "cache_status": "miss"
    }

# Weather tools
@mcp.tool()
async def get_current_weather(location: str, units: str = "celsius") -> Dict:
    """
    Get current weather for a location
    
    Args:
        location: City name (e.g., 'San Francisco, CA')
        units: Temperature units ('celsius', 'fahrenheit', 'kelvin')
        
    Returns:
        Dictionary with current weather data
    """
    try:
        # First check resource cache
        cache = await get_weather_resource(location)
        
        # Convert units for API
        api_units = {"celsius": "metric", "fahrenheit": "imperial", "kelvin": "standard"}
        unit_param = api_units.get(units, "metric")
        
        # Simulated API call (replace with real API in production)
        weather_data = {
            "name": location,
            "main": {
                "temp": 22.5,
                "humidity": 65
            },
            "weather": [{"description": "partly cloudy"}],
            "wind": {"speed": 3.2}
        }
        
        return {
            "success": True,
            "data": {
                "location": weather_data["name"],
                "temperature": weather_data["main"]["temp"],
                "description": weather_data["weather"][0]["description"].title(),
                "humidity": weather_data["main"]["humidity"],
                "wind_speed": weather_data["wind"]["speed"],
                "units": units,
                "timestamp": datetime.now().isoformat(),
                "cache_info": cache
            }
        }
        
    except Exception as e:
        logging.error(f"Weather API error: {e}")
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

@mcp.tool()
async def get_weather_forecast(location: str, days: int = 3) -> Dict:
    """
    Get weather forecast for a location
    
    Args:
        location: City name (e.g., 'San Francisco, CA')
        days: Number of forecast days (1-5)
        
    Returns:
        Dictionary with forecast data
    """
    try:
        forecasts = []
        current_time = datetime.now().timestamp()
        
        for i in range(days):
            day_timestamp = current_time + (i * 24 * 60 * 60)
            forecasts.append({
                "date": datetime.fromtimestamp(day_timestamp).strftime("%Y-%m-%d"),
                "temperature_high": 25.0 - i,
                "temperature_low": 18.0 - i,
                "description": f"Day {i+1} forecast",
                "humidity": 60 + i * 2
            })
        
        return {
            "success": True,
            "data": {
                "location": location,
                "forecast": forecasts,
                "days": len(forecasts)
            }
        }
        
    except Exception as e:
        logging.error(f"Forecast API error: {e}")
        return {
            "success": False,
            "error": str(e),
            "prompt": "error_prompt"
        }

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the MCP server
    print("🌤️  Starting Weather MCP Server...")
    mcp.run(transport="streamable-http") 