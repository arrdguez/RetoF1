from typing import Dict, Any, List
from config.settings import SCORING_CONFIG

class ChallengeScorer:
    """
    Computes points earned in the 'Desafío Tech: Estratega de F1' challenge
    based on predicted vs actual results.
    """

    def __init__(self, scoring_config=SCORING_CONFIG):
        self.cfg = scoring_config

    def score_prediction(
        self,
        predicted: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        predicted format:
        {
            "pole": "VER",
            "p1": "VER",
            "p2": "NOR",
            "p3": "LEC",
            "fastest_lap": "NOR",
            "checo_position": "P5",  # or "DNF"
            "safety_cars": 1
        }
        """
        breakdown = {}
        total_points = 0

        # 1. Pole Position (10 pts)
        pole_match = predicted.get("pole", "").upper() == actual.get("pole", "").upper()
        pts_pole = self.cfg.pole_exact if pole_match else 0
        breakdown["pole_position"] = {
            "predicted": predicted.get("pole"),
            "actual": actual.get("pole"),
            "matched": pole_match,
            "points": pts_pole,
            "max": self.cfg.pole_exact
        }
        total_points += pts_pole

        # 2. Podium (Winner 15 pts, P2 10 pts, P3 10 pts, or 5 pts each if in podium different position)
        act_p1 = actual.get("p1", "").upper()
        act_p2 = actual.get("p2", "").upper()
        act_p3 = actual.get("p3", "").upper()
        actual_podium = [act_p1, act_p2, act_p3]

        pred_p1 = predicted.get("p1", "").upper()
        pred_p2 = predicted.get("p2", "").upper()
        pred_p3 = predicted.get("p3", "").upper()

        pts_p1 = self.cfg.winner_exact if pred_p1 == act_p1 else (self.cfg.podium_other_position if pred_p1 in actual_podium else 0)
        pts_p2 = self.cfg.second_exact if pred_p2 == act_p2 else (self.cfg.podium_other_position if pred_p2 in actual_podium else 0)
        pts_p3 = self.cfg.third_exact if pred_p3 == act_p3 else (self.cfg.podium_other_position if pred_p3 in actual_podium else 0)

        breakdown["podio_1st"] = {"predicted": pred_p1, "actual": act_p1, "points": pts_p1, "max": self.cfg.winner_exact}
        breakdown["podio_2nd"] = {"predicted": pred_p2, "actual": act_p2, "points": pts_p2, "max": self.cfg.second_exact}
        breakdown["podio_3rd"] = {"predicted": pred_p3, "actual": act_p3, "points": pts_p3, "max": self.cfg.third_exact}
        total_points += (pts_p1 + pts_p2 + pts_p3)

        # 3. Vuelta Rápida (10 pts)
        fl_match = predicted.get("fastest_lap", "").upper() == actual.get("fastest_lap", "").upper()
        pts_fl = self.cfg.fastest_lap_exact if fl_match else 0
        breakdown["vuelta_rapida"] = {
            "predicted": predicted.get("fastest_lap"),
            "actual": actual.get("fastest_lap"),
            "matched": fl_match,
            "points": pts_fl,
            "max": self.cfg.fastest_lap_exact
        }
        total_points += pts_fl

        # 4. Posición de Checo Pérez (15 pts)
        def norm_pos(val):
            s = str(val).strip().upper()
            return s if s.startswith("P") or s == "DNF" else f"P{s}"

        checo_match = norm_pos(predicted.get("checo_position", "")) == norm_pos(actual.get("checo_position", ""))
        pts_checo = self.cfg.checo_position_exact if checo_match else 0
        breakdown["checo_position"] = {
            "predicted": predicted.get("checo_position"),
            "actual": actual.get("checo_position"),
            "matched": checo_match,
            "points": pts_checo,
            "max": self.cfg.checo_position_exact
        }
        total_points += pts_checo

        # 5. Safety Cars físicos (10 pts)
        sc_match = int(predicted.get("safety_cars", -1)) == int(actual.get("safety_cars", -2))
        pts_sc = self.cfg.safety_cars_exact if sc_match else 0
        breakdown["safety_cars"] = {
            "predicted": predicted.get("safety_cars"),
            "actual": actual.get("safety_cars"),
            "matched": sc_match,
            "points": pts_sc,
            "max": self.cfg.safety_cars_exact
        }
        total_points += pts_sc

        return {
            "total_score": total_points,
            "max_possible": self.cfg.max_possible_points,
            "accuracy_pct": round((total_points / self.cfg.max_possible_points) * 100, 1),
            "breakdown": breakdown
        }
