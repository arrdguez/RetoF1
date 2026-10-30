import json
from pathlib import Path
from typing import Dict, Any, List
from config.settings import PROCESSED_DATA_DIR, SAMPLES_DATA_DIR

class RecentFormAnalyzer:
    """
    Analyzes telemetry, results, and reliability trends from the last 3 races.
    Dynamically ingests real processed data from FastF1/Ergast.
    Applies exponential recency weighting: Race N (50%), Race N-1 (30%), Race N-2 (20%).
    """

    def __init__(self, data_path: Path = None):
        real_path = PROCESSED_DATA_DIR / "last_3_races_real.json"
        sample_path = SAMPLES_DATA_DIR / "last_3_races.json"
        self.data_path = data_path or (real_path if real_path.exists() else sample_path)
        self.races_data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"races": []}

    def calculate_driver_form_boosts(self) -> Dict[str, float]:
        """
        Dynamically calculates driver performance multipliers based on real finishes,
        podiums, and poles across the last 3 races using 50%/30%/20% recency weighting.
        """
        races = self.races_data.get("races", [])
        if not races:
            # Fallback baseline
            return {"LEC": 1.04, "NOR": 1.03, "VER": 1.02, "SAI": 1.03, "PIA": 1.02, "RUS": 1.00, "HAM": 0.99, "PER": 0.97}

        weights = [0.20, 0.30, 0.50]  # Oldest to newest
        driver_scores: Dict[str, float] = {}

        # Points mapping for finishing position (1st=25, 2nd=18, 3rd=15, etc.)
        points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

        # Track appearances
        all_drivers = {"VER", "NOR", "LEC", "SAI", "PIA", "RUS", "HAM", "PER", "ALO", "HUL", "TSU", "ALB"}

        for w, r in zip(weights, races[-3:]):
            pole = r.get("pole")
            winner = r.get("winner")
            podium = r.get("podium", [])
            checo_finish = r.get("checo_finish")

            for d in all_drivers:
                pts = 0.0
                if d == winner:
                    pts += 25.0
                elif len(podium) > 1 and d == podium[1]:
                    pts += 18.0
                elif len(podium) > 2 and d == podium[2]:
                    pts += 15.0

                if d == pole:
                    pts += 5.0  # Bonus for pole pace

                if d == "PER" and checo_finish and isinstance(checo_finish, int):
                    pts = max(pts, points_map.get(checo_finish, 0.0))

                driver_scores[d] = driver_scores.get(d, 0.0) + (pts * w)

        # Normalize into multipliers centered around 1.00 (range 0.96 to 1.05)
        max_score = max(driver_scores.values()) if driver_scores else 25.0
        boosts = {}
        for d, score in driver_scores.items():
            norm = (score / max_score) if max_score > 0 else 0.5
            multiplier = round(0.96 + (norm * 0.09), 3)
            boosts[d] = multiplier

        return boosts

    def get_team_trends(self) -> Dict[str, str]:
        return {
            "Ferrari": "Alta inercia competitiva (Victoria en Austin, pole en Baku, tracción superior)",
            "McLaren": "Líder en consistencia y balance aerodinámico (Victoria en Singapur, pole en Austin)",
            "Red Bull": "Velocidad punta máxima en recta; ventaja histórica de Verstappen en México",
            "Mercedes": "Sensibilidad térmica elevada bajo los 44°C de asfalto"
        }
