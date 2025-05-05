import requests
from datetime import datetime, timedelta

def fetch_weather(lat, lon, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,windspeed_10m,snowfall,weathercode,cloudcover,sunshine_duration",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    return response.json()