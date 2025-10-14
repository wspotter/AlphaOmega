"""
Simple Weather Tool Server for OpenWebUI
A minimal FastAPI server that provides a weather lookup tool.
This demonstrates the native OpenAPI integration pattern.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import uvicorn

# Initialize FastAPI app with metadata for OpenAPI schema
app = FastAPI(
    title="Weather Tool Server",
    description="A simple weather lookup tool for OpenWebUI integration",
    version="1.0.0",
)


class WeatherRequest(BaseModel):
    """Request model for weather lookup"""
    city: str = Field(
        ...,
        description="The name of the city to get weather information for",
        example="New York"
    )


class WeatherResponse(BaseModel):
    """Response model for weather data"""
    city: str = Field(description="The city name")
    temperature: str = Field(description="Current temperature")
    conditions: str = Field(description="Weather conditions")
    humidity: str = Field(description="Humidity percentage")
    wind_speed: str = Field(description="Wind speed")


# Mock weather data for demonstration
MOCK_WEATHER_DATA: Dict[str, Dict[str, str]] = {
    "new york": {
        "temperature": "72°F (22°C)",
        "conditions": "Partly Cloudy",
        "humidity": "65%",
        "wind_speed": "10 mph"
    },
    "london": {
        "temperature": "59°F (15°C)",
        "conditions": "Rainy",
        "humidity": "80%",
        "wind_speed": "15 mph"
    },
    "tokyo": {
        "temperature": "68°F (20°C)",
        "conditions": "Sunny",
        "humidity": "55%",
        "wind_speed": "8 mph"
    },
    "paris": {
        "temperature": "64°F (18°C)",
        "conditions": "Overcast",
        "humidity": "70%",
        "wind_speed": "12 mph"
    },
    "sydney": {
        "temperature": "75°F (24°C)",
        "conditions": "Clear",
        "humidity": "60%",
        "wind_speed": "14 mph"
    }
}


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with server information"""
    return {
        "message": "Weather Tool Server",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.post(
    "/get_weather",
    response_model=WeatherResponse,
    summary="Get current weather for a city",
    description="Retrieves current weather information for a specified city. "
                "This is a mock implementation for demonstration purposes."
)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    """
    Get weather information for a specified city.
    
    Args:
        request: WeatherRequest containing the city name
        
    Returns:
        WeatherResponse with current weather data
        
    Raises:
        HTTPException: If the city is not found in the database
    """
    city_lower = request.city.lower().strip()
    
    # Check if city exists in our mock database
    if city_lower not in MOCK_WEATHER_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Weather data not available for '{request.city}'. "
                   f"Available cities: {', '.join(MOCK_WEATHER_DATA.keys())}"
        )
    
    weather_data = MOCK_WEATHER_DATA[city_lower]
    
    return WeatherResponse(
        city=request.city,
        temperature=weather_data["temperature"],
        conditions=weather_data["conditions"],
        humidity=weather_data["humidity"],
        wind_speed=weather_data["wind_speed"]
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

