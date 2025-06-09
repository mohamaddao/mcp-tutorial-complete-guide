# 🌤️ Weather MCP Server Example

A complete example of an MCP server that provides weather information. This demonstrates real-world MCP patterns including API integration, error handling, and proper response formatting.

## 🎯 Features

- **Current Weather**: Get real-time weather data for any location
- **Weather Forecast**: Get multi-day weather forecasts
- **Unit Conversion**: Support for Celsius, Fahrenheit, and Kelvin
- **Error Handling**: Robust error handling and validation
- **Async Support**: Full async/await implementation

## 🚀 Quick Start

```bash
# Navigate to the weather MCP directory
cd examples/weather_mcp

# Install dependencies
pip install httpx pydantic

# Run the demo
python weather_server.py
```

## 🔧 Available Tools

### 1. `get_current_weather`
Get current weather conditions for a specified location.

**Parameters:**
- `location` (required): City name (e.g., "San Francisco, CA")
- `units` (optional): Temperature units - "celsius", "fahrenheit", or "kelvin"

**Example Request:**
```json
{
  "tool_name": "get_current_weather",
  "arguments": {
    "location": "San Francisco, CA",
    "units": "celsius"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "location": "San Francisco, CA",
    "temperature": 22.5,
    "description": "Partly Cloudy",
    "humidity": 65,
    "wind_speed": 3.2,
    "units": "celsius",
    "timestamp": "2025-06-15T10:30:00"
  },
  "message": "Current weather for San Francisco, CA"
}
```

### 2. `get_weather_forecast`
Get weather forecast for multiple days.

**Parameters:**
- `location` (required): City name (e.g., "New York, NY")
- `days` (optional): Number of forecast days (1-5, default: 3)

**Example Request:**
```json
{
  "tool_name": "get_weather_forecast",
  "arguments": {
    "location": "New York, NY",
    "days": 3
  }
}
```

## 🔗 Integration with Real Weather APIs

To use real weather data, replace the simulated API calls with actual weather service integration:

```python
async def _fetch_weather_data(self, location: str, units: str) -> Dict[str, Any]:
    """Fetch current weather data from OpenWeatherMap API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{self.base_url}/weather",
            params={
                "q": location,
                "appid": self.api_key,
                "units": units
            }
        )
        response.raise_for_status()
        return response.json()
```

## 🔑 API Key Setup

For production use with OpenWeatherMap:

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Set environment variable:
   ```bash
   export OPENWEATHER_API_KEY="your_api_key_here"
   ```
4. Update the server initialization:
   ```python
   import os
   weather_server = WeatherMCPServer(api_key=os.getenv("OPENWEATHER_API_KEY"))
   ```

## 🛡️ Error Handling

The server includes comprehensive error handling:

- **Network Errors**: Graceful handling of API failures
- **Invalid Locations**: Clear error messages for unknown locations
- **Rate Limiting**: Proper handling of API rate limits
- **Validation**: Input parameter validation

## 📈 Extending the Server

Add new weather-related tools:

```python
async def get_weather_alerts(self, location: str) -> Dict[str, Any]:
    """Get weather alerts and warnings"""
    # Implementation here
    pass

async def get_historical_weather(self, location: str, date: str) -> Dict[str, Any]:
    """Get historical weather data"""
    # Implementation here
    pass
```

## 🎓 Learning Objectives

This example demonstrates:

- **MCP Server Architecture**: Proper structure and organization
- **Tool Registration**: How to register and describe tools
- **Async Programming**: Using async/await for API calls
- **Error Handling**: Robust error handling patterns
- **Response Formatting**: Consistent response structures
- **Input Validation**: Parameter validation and type checking

## 🚀 Next Steps

- Explore the [Database MCP Example](../database_manager/)
- Learn about [File Processing MCP](../file_processor/)
- Study [Advanced Security Patterns](../../notebooks/advanced/13_security_auth.ipynb)

---

**Ready to build your own weather integrations? Start with the [API Integration tutorial](../../notebooks/intermediate/07_api_integration.ipynb)!** 