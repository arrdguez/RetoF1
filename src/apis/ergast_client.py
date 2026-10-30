import logging
import json
import requests
from typing import Optional, Dict, Any, List
from config.settings import SAMPLES_DATA_DIR

logger = logging.getLogger(__name__)

class ErgastClient:
    """
    Client for Ergast / Jolpica F1 historical API.
    Used for retrieving driver standings, race results, and historical Mexico GP stats.
    """
    BASE_URL = "https://api.jolpica.net/ergast/f1"
    BACKUP_URL = "https://ergast.com/api/f1"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _get(self, path: str) -> Dict[str, Any]:
        endpoint = path.strip("/")
        for base in [self.BASE_URL, self.BACKUP_URL]:
            url = f"{base}/{endpoint}.json"
            try:
                res = requests.get(url, timeout=self.timeout)
                if res.status_code == 200:
                    return res.json().get("MRData", {})
            except Exception as e:
                logger.debug("Failed requesting %s: %s", url, e)
        return {}

    def get_mexico_gp_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves recent Mexico Grand Prix race results.
        """
        data = self._get(f"circuits/rodriguez/results?limit={limit*20}")
        races = data.get("RaceTable", {}).get("Races", [])
        if not races:
            sample_path = SAMPLES_DATA_DIR / "mexico_gp_history.json"
            if sample_path.exists():
                with open(sample_path, "r", encoding="utf-8") as f:
                    return json.load(f).get("historical_editions", [])
        return races

    def get_last_3_races(self) -> Dict[str, Any]:
        """
        Retrieves results of the 3 most recent races for momentum analysis.
        """
        sample_path = SAMPLES_DATA_DIR / "last_3_races.json"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"races": []}
