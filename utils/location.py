# utils/location.py
import requests

def get_current_location() -> dict:
    """
    Returns a dict with keys: city, country_code, latitude, longitude.
    Uses ipapi.co.
    """
    resp = requests.get("https://ipapi.co/json/", timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return {
        "city": data.get("city"),
        "country": data.get("country_code"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
    }
