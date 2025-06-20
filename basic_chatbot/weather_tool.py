import requests
from langchain.tools import tool

@tool
def get_weather_from_wttr_in(location: str) -> str:
    """
    Fetches a simplified weather report from wttr.in for the given location.
    Note: This relies on a public web service and might be rate-limited or change.
    """
    try:
        # wttr.in can return plain text, useful for quick checks
        response = requests.get(f"https://wttr.in/{location}?format=%l:+%c+%t")
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return f"Could not fetch weather: {e}"

# You could then add get_weather_from_wttr_in to your tools list.
