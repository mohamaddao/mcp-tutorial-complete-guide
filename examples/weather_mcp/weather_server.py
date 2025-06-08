#!/usr/bin/env python3
"""
Weather MCP Server Example

This example demonstrates a complete MCP server that provides weather information
using a real weather API. It showcases:
- Proper MCP server structure
- API integration patterns
- Error handling
- Input validation
- Response formatting

Usage:
    python weather_server.py

Requirements:
    pip install mcp uvicorn fastapi httpx pydantic
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx
from pydantic import BaseModel, ValidationError

# In a real implementation, you'd import these from the MCP library
# For this example, we'll use simplified versions

class WeatherData(BaseModel):
    """Weather data model"""
    location: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    timestamp: datetime

class WeatherMCPServer:
    """Weather MCP Server providing weather information tools"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"  # In production, use environment variable
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
        
        # Register our tools
        self.tools = {
            "get_current_weather": {
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name (e.g., 'San Francisco, CA')"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit", "kelvin"],
                            "default": "celsius",
                            "description": "Temperature units"
                        }
                    },
                    "required": ["location"]
                },
                "handler": self.get_current_weather
            },
            "get_weather_forecast": {
                "description": "Get 5-day weather forecast for a location",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name (e.g., 'San Francisco, CA')"
                        },
                        "days": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                            "default": 3,
                            "description": "Number of forecast days (1-5)"
                        }
                    },
                    "required": ["location"]
                },
                "handler": self.get_weather_forecast
            }
        }
    
    async def get_current_weather(self, location: str, units: str = "celsius") -> Dict[str, Any]:
        """Get current weather for a location"""
        try:
            # Convert units for API
            api_units = {"celsius": "metric", "fahrenheit": "imperial", "kelvin": "standard"}
            unit_param = api_units.get(units, "metric")
            
            # Make API request (simulated for demo)
            weather_data = await self._fetch_weather_data(location, unit_param)
            
            # Format response
            result = {
                "location": weather_data["name"],
                "temperature": weather_data["main"]["temp"],
                "description": weather_data["weather"][0]["description"].title(),
                "humidity": weather_data["main"]["humidity"],
                "wind_speed": weather_data["wind"]["speed"],
                "units": units,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": result,
                "message": f"Current weather for {result['location']}"
            }
            
        except Exception as e:
            self.logger.error(f"Weather API error: {e}")
            return {
                "success": False,
                "error": f"Unable to fetch weather data: {str(e)}",
                "message": "Weather service temporarily unavailable"
            }
    
    async def get_weather_forecast(self, location: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        try:
            # Simulate forecast data (in real implementation, call forecast API)
            forecast_data = await self._fetch_forecast_data(location, days)
            
            forecasts = []
            for day_data in forecast_data["list"][:days]:
                forecasts.append({
                    "date": datetime.fromtimestamp(day_data["dt"]).strftime("%Y-%m-%d"),
                    "temperature_high": day_data["main"]["temp_max"],
                    "temperature_low": day_data["main"]["temp_min"],
                    "description": day_data["weather"][0]["description"].title(),
                    "humidity": day_data["main"]["humidity"]
                })
            
            return {
                "success": True,
                "data": {
                    "location": location,
                    "forecast": forecasts,
                    "days": len(forecasts)
                },
                "message": f"{days}-day forecast for {location}"
            }
            
        except Exception as e:
            self.logger.error(f"Forecast API error: {e}")
            return {
                "success": False,
                "error": f"Unable to fetch forecast: {str(e)}",
                "message": "Forecast service temporarily unavailable"
            }
    
    async def _fetch_weather_data(self, location: str, units: str) -> Dict[str, Any]:
        """Fetch current weather data from API (simulated)"""
        # In a real implementation, this would make an HTTP request:
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"{self.base_url}/weather", 
        #                                params={"q": location, "appid": self.api_key, "units": units})
        #     return response.json()
        
        # Simulated response for demo
        return {
            "name": location,
            "main": {
                "temp": 22.5,
                "humidity": 65,
                "temp_max": 25.0,
                "temp_min": 18.0
            },
            "weather": [{"description": "partly cloudy"}],
            "wind": {"speed": 3.2}
        }
    
    async def _fetch_forecast_data(self, location: str, days: int) -> Dict[str, Any]:
        """Fetch forecast data from API (simulated)"""
        # Simulated forecast response
        import time
        current_time = int(time.time())
        
        forecast_list = []
        for i in range(days):
            day_timestamp = current_time + (i * 24 * 60 * 60)  # Add days
            forecast_list.append({
                "dt": day_timestamp,
                "main": {
                    "temp_max": 25.0 - i,
                    "temp_min": 18.0 - i,
                    "humidity": 60 + i * 2
                },
                "weather": [{"description": f"day {i+1} weather"}]
            })
        
        return {"list": forecast_list}
    
    def list_tools(self) -> List[str]:
        """Return list of available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        return self.tools.get(tool_name)

async def main():
    """Demo the weather MCP server"""
    # Create server
    weather_server = WeatherMCPServer()
    
    print("🌤️  Weather MCP Server Demo")
    print("=" * 40)
    
    # List available tools
    print(f"📋 Available tools: {weather_server.list_tools()}")
    print()
    
    # Test current weather
    print("🔍 Testing current weather...")
    result = await weather_server.get_current_weather("San Francisco, CA")
    print(f"✅ Result: {result}")
    print()
    
    # Test forecast
    print("🔍 Testing weather forecast...")
    result = await weather_server.get_weather_forecast("New York, NY", days=3)
    print(f"✅ Result: {result}")
    print()
    
    print("🎉 Weather MCP Server demo completed!")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the demo
    asyncio.run(main()) 