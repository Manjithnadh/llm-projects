import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()
API_KEY = os.getenv("WEATHERSTACK_API_KEY")

@tool
def get_weatherstack_weather(city: str) -> str:
    """Get current weather from Weatherstack API for a given city."""
    url = f"http://api.weatherstack.com/current?access_key={}&query={city}"
    try:
        response = requests.get(url)
        data = response.json()

        if 'error' in data:
            return f"Error: {data['error']['info']}"

        condition = data['current']['weather_descriptions'][0]
        temp = data['current']['temperature']
        humidity = data['current']['humidity']
        return f"In {city}, it's {condition} with {temp}°C and {humidity}% humidity."
    except Exception as e:
        return f"Failed to fetch weather data: {e}"