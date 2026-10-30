import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import pandas as pd
from config.settings import CACHE_DIR, SAMPLES_DATA_DIR

logger = logging.getLogger(__name__)

class FastF1Client:
    """
    Client for extracting official F1 timing, results, and telemetry using FastF1 and Ergast.
    Does not require account credentials for race results, qualifying, or standings.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or CACHE_DIR
        self._init_fastf1()

    def _init_fastf1(self):
        try:
            import fastf1
            from fastf1.ergast import Ergast
            fastf1.Cache.enable_cache(str(self.cache_dir))
            self.fastf1 = fastf1
            self.ergast = Ergast()
            self.is_available = True
            logger.info("FastF1 initialized with cache at %s", self.cache_dir)
        except Exception as e:
            logger.warning("FastF1 initialization notice: %s", e)
            self.is_available = False
            self.ergast = None

    def get_race_results(self, season: int, round_num: int) -> Optional[pd.DataFrame]:
        """
        Retrieves full official race classification for a given season and round.
        """
        if not self.is_available or not self.ergast:
            return None
        try:
            res = self.ergast.get_race_results(season=season, round=round_num)
            if res and res.content:
                return res.content[0]
        except Exception as e:
            logger.error("Error fetching race results for %s R%s: %s", season, round_num, e)
        return None

    def get_qualifying_results(self, season: int, round_num: int) -> Optional[pd.DataFrame]:
        """
        Retrieves official qualifying results with Q1, Q2, Q3 times.
        """
        if not self.is_available or not self.ergast:
            return None
        try:
            res = self.ergast.get_qualifying_results(season=season, round=round_num)
            if res and res.content:
                return res.content[0]
        except Exception as e:
            logger.error("Error fetching qualifying results for %s R%s: %s", season, round_num, e)
        return None

    def get_driver_standings(self, season: int) -> Optional[pd.DataFrame]:
        """
        Retrieves current championship standings.
        """
        if not self.is_available or not self.ergast:
            return None
        try:
            res = self.ergast.get_driver_standings(season=season)
            if res and res.content:
                return res.content[0]
        except Exception as e:
            logger.error("Error fetching driver standings for %s: %s", season, e)
        return None
