import logging
import json
import requests
from typing import Optional, Dict, Any, List
from config.settings import SAMPLES_DATA_DIR

logger = logging.getLogger(__name__)

class OpenF1Client:
    """
    Client for OpenF1 public REST API (https://api.openf1.org/v1/).
    Provides real-time and historical timing, laps, intervals, and weather data.
    """
    BASE_URL = "https://api.openf1.org/v1"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("OpenF1 request error (%s): %s", url, e)
            return []

    def get_sessions(self, country_name: str = "Mexico", year: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {"country_name": country_name}
        if year:
            params["year"] = year
        data = self._get("sessions", params)
        if not data:
            # Fallback to local sample
            sample_path = SAMPLES_DATA_DIR / "mexico_gp_history.json"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    return [json.load(f)]
        return data

    def get_laps(self, session_key: int, driver_number: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        return self._get("laps", params)

    def get_weather(self, session_key: int) -> List[Dict[str, Any]]:
        return self._get("weather", {"session_key": session_key})
