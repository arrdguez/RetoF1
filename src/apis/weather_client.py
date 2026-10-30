import logging
import json
import requests
from typing import Dict, Any
from config.settings import SAMPLES_DATA_DIR

logger = logging.getLogger(__name__)

class WeatherClient:
    """
    Client for track weather conditions at Autódromo Hermanos Rodríguez, CDMX.
    Uses Open-Meteo free API with local sample fallback.
    """
    # Autódromo Hermanos Rodríguez coordinates
    LATITUDE = 19.4042
    LONGITUDE = -99.0907
    ELEVATION = 2240

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_mexico_city_forecast(self) -> Dict[str, Any]:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.LATITUDE,
            "longitude": self.LONGITUDE,
            "elevation": self.ELEVATION,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,surface_pressure,wind_speed_10m",
            "forecast_days": 3,
            "timezone": "America/Mexico_City"
        }
        try:
            res = requests.get(url, params=params, timeout=self.timeout)
            if res.status_code == 200:
                data = res.json()
                return {
                    "source": "open-meteo",
                    "latitude": data.get("latitude"),
                    "longitude": data.get("longitude"),
                    "elevation": data.get("elevation"),
                    "hourly": data.get("hourly")
                }
        except Exception as e:
            logger.debug("Weather API unavailable: %s. Using local sample.", e)

        sample_path = SAMPLES_DATA_DIR / "weather_mexico_gp.json"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"source": "fallback", "temp": 23.0, "rain_prob": 15}
