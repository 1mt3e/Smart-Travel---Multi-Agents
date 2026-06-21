import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Default Models
ITINERARY_MODEL = "gemini-flash-latest"  # Highly capable model for planning
UTILITY_MODEL = "gemini-flash-latest" # Extremely fast and cost-efficient for sub-tasks

# OpenWeatherMap config
DEFAULT_LAT_LON = {
    "Quy Nhơn": {"lat": 13.783, "lon": 109.233},
    "Gia Lai": {"lat": 13.983, "lon": 107.983},
    "Đà Lạt": {"lat": 11.940, "lon": 108.458},
    "Huế": {"lat": 16.463, "lon": 107.590},
    "Phú Quốc": {"lat": 10.289, "lon": 103.984}
}

def get_gemini_api_key(streamlit_key=None):
    """Returns the Gemini API key, giving priority to UI input, then env variables."""
    if streamlit_key:
        return streamlit_key
    return os.getenv("GEMINI_API_KEY", "")

def get_weather_api_key(streamlit_key=None):
    """Returns the OpenWeatherMap API key."""
    if streamlit_key:
        return streamlit_key
    return os.getenv("OPENWEATHER_API_KEY", "")
