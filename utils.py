# utils.py
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

geolocator = Nominatim(user_agent="nisar-weather-app")

def geocode_location(text):
    """
    Accepts: city name, zip code, "lat,lon" or landmark string.
    Returns: (lat, lon, display_name) or None
    """
    text = text.strip()
    # Coordinates?
    if "," in text:
        parts = text.split(",")
        try:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return lat, lon, f"{lat:.4f},{lon:.4f}"
        except ValueError:
            pass

    # Try geopy (Nominatim)
    try:
        location = geolocator.geocode(text, exactly_one=True, timeout=10)
        if location:
            return location.latitude, location.longitude, location.address
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    return None

def get_ip_location():
    """
    Uses ipinfo.io to get approximate user location (IP-based).
    """
    try:
        r = requests.get("https://ipinfo.io/json", timeout=8)
        if r.status_code == 200:
            data = r.json()
            loc = data.get("loc")
            if loc:
                lat, lon = map(float, loc.split(","))
                city = data.get("city", "")
                region = data.get("region", "")
                country = data.get("country", "")
                name = ", ".join([p for p in [city, region, country] if p])
                return lat, lon, name or f"{lat:.4f},{lon:.4f}"
    except Exception:
        return None, None, None
    return None, None, None

def fetch_current_weather(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def fetch_5day_forecast(lat, lon, api_key):
    # 5 day / 3 hour forecast
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None
