import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import CACHE_DIR, SAMPLES_DATA_DIR

logger = logging.getLogger(__name__)

class FastF1Client:
    """
    Client for extracting official F1 timing and telemetry data using FastF1.
    Provides graceful fallback to sample/offline data if offline or library missing.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self._fastf1_available = False
        self._init_fastf1()

    def _init_fastf1(self):
        try:
            import fastf1
            fastf1.Cache.enable_cache(str(self.cache_dir))
            self._fastf1 = fastf1
            self._fastf1_available = True
            logger.info("FastF1 initialized with cache at %s", self.cache_dir)
        except ImportError:
            logger.warning("FastF1 library not installed. Using local sample fallback.")
            self._fastf1_available = False

    def load_session(self, year: int, race_round_or_name: Any, session_type: str = "Q"):
        """
        Loads a session (e.g. 'FP1', 'FP2', 'FP3', 'Q', 'R').
        """
        if not self._fastf1_available:
            return self._get_fallback_session(year, race_round_or_name, session_type)

        try:
            session = self._fastf1.get_session(year, race_round_or_name, session_type)
            session.load()
            return session
        except Exception as e:
            logger.warning("Failed to load FastF1 session: %s. Falling back to local data.", e)
            return self._get_fallback_session(year, race_round_or_name, session_type)

    def _get_fallback_session(self, year: int, race: Any, session_type: str) -> Dict[str, Any]:
        sample_path = SAMPLES_DATA_DIR / "mexico_gp_history.json"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"status": "mock", "year": year, "race": str(race), "session": session_type}

    def get_drivers_info(self) -> list:
        sample_path = SAMPLES_DATA_DIR / "drivers_teams.json"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
