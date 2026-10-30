from dataclasses import dataclass
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"
CACHE_DIR = BASE_DIR / "fastf1_cache"

# Ensure directories exist
for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLES_DATA_DIR, CACHE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class CircuitConfig:
    name: str = "Autódromo Hermanos Rodríguez"
    country: str = "Mexico"
    city: str = "Mexico City"
    altitude_meters: float = 2240.0
    air_density_ratio: float = 0.78  # ~78% of sea-level density
    track_length_km: float = 4.304
    laps: int = 71
    race_distance_km: float = 305.354
    turn_1_distance_meters: float = 890.0  # Longest run to Turn 1 on the calendar
    historical_sc_probability: float = 0.70  # ~70% chance of physical Safety Car


@dataclass(frozen=True)
class ChallengeScoring:
    pole_exact: int = 10
    winner_exact: int = 15
    second_exact: int = 10
    third_exact: int = 10
    podium_other_position: int = 5
    fastest_lap_exact: int = 10
    checo_position_exact: int = 15
    safety_cars_exact: int = 10
    max_possible_points: int = 80


CIRCUIT_CONFIG = CircuitConfig()
SCORING_CONFIG = ChallengeScoring()
