import sys
import json
import argparse
from typing import Dict, Any

from src.models.predictor import F1RacePredictor
from src.features.altitude_physics import AltitudePhysicsModel
from src.evaluation.scoring import ChallengeScorer
from src.prompts.copilot_assistant import CopilotPromptGenerator

def print_banner():
    banner = """
========================================================================
🏁  DESAFÍO TECH: CONVIÉRTETE EN EL 'ESTRATEGA DE F1' CON GITHUB STACK  🏁
   Autódromo Hermanos Rodríguez | Gran Premio de México (2,240m ASL)
========================================================================
"""
    print(banner)

def run_predictions(n_sim: int = 2500):
    print(f"\n[+] Ejecutando simulación Monte Carlo ({n_sim} iteraciones)...")
    predictor = F1RacePredictor(n_simulations=n_sim)
    pred_data = predictor.generate_full_prediction()
    q = pred_data["quiniela_predictions"]

    print("\n" + "="*70)
    print("📊 PRONÓSTICO OFICIAL DE LA QUINIELA (5 PUNTOS CLAVE)")
    print("="*70)

    # 1. Pole Position
    pole = q["1_pole_position"]
    print(f"\n1️⃣  POLE POSITION (Sábado Q3) -> {pole['challenge_points']} pts")
    print(f"    ▶ Piloto Proyectado: {pole['driver']} (Probabilidad: {pole['probability_pct']}%)")
    print(f"    ▶ Principales candidatos: {pole['top_contenders']}")
    print(f"    ▶ Lógica: {pole['rationale']}")

    # 2. Podio Oficial
    podium = q["2_podio_oficial"]
    print(f"\n2️⃣  PODIO OFICIAL EXACTO (Domingo) -> Hasta {podium['challenge_points']} pts")
    print(f"    ▶ 1° Lugar (Ganador, 15 pts): {podium['p1_winner']} (Prob: {podium['p1_prob_pct']}%)")
    print(f"    ▶ 2° Lugar (10 pts):          {podium['p2_second']} (Prob: {podium['p2_prob_pct']}%)")
    print(f"    ▶ 3° Lugar (10 pts):          {podium['p3_third']} (Prob: {podium['p3_prob_pct']}%)")
    print(f"    ▶ Secuencia exacta proyectada: {' -> '.join(podium['exact_podium_sequence'])}")
    print(f"    ▶ Lógica: {podium['rationale']}")

    # 3. Vuelta Rápida
    fl = q["3_vuelta_rapida"]
    print(f"\n3️⃣  VUELTA RÁPIDA -> {fl['challenge_points']} pts")
    print(f"    ▶ Piloto Proyectado: {fl['driver']} (Probabilidad: {fl['probability_pct']}%)")
    print(f"    ▶ Candidatos: {fl['top_contenders']}")
    print(f"    ▶ Lógica: {fl['rationale']}")

    # 4. Checo Pérez
    checo = q["4_posicion_checo_perez"]
    print(f"\n4️⃣  POSICIÓN EXACTA DE CHECO PÉREZ -> {checo['challenge_points']} pts")
    print(f"    ▶ Pronóstico: {checo['predicted_finish']} (Probabilidad: {checo['probability_pct']}%)")
    print("    ▶ Distribución:")
    for cand in checo['alternatives']:
        print(f"        - {cand['position']}: {cand['probability_pct']}%")
    print(f"    ▶ Lógica: {checo['rationale']}")

    # 5. Safety Cars
    sc = q["5_safety_cars_fisicos"]
    print(f"\n5️⃣  SAFETY CARS FÍSICOS (No VSC) -> {sc['challenge_points']} pts")
    print(f"    ▶ Conteo Exacto Proyectado: {sc['predicted_count']} auto(s) (Probabilidad: {sc['mode_probability_pct']}%)")
    print("    ▶ Distribución esperada:")
    for k, v in sc['distribution'].items():
        print(f"        - {k}: {v}")
    print(f"    ▶ Lógica: {sc['rationale']}")

    print("\n" + "="*70)
    print(f"🎯 PUNTOS MÁXIMOS POSIBLES: {pred_data['total_potential_points']} pts")
    print("="*70)
    return pred_data

def run_physics():
    print("\n[+] Analizando Física Aerodinámica y Refrigeración a 2,240m de altitud...")
    phys = AltitudePhysicsModel()
    summary = phys.get_altitude_impact_summary()
    print(json.dumps(summary, indent=4))

def run_scoring_demo():
    print("\n[+] Demostración de Sistema de Puntuación Oficial...")
    scorer = ChallengeScorer()
    mock_prediction = {
        "pole": "LEC",
        "p1": "VER",
        "p2": "NOR",
        "p3": "LEC",
        "fastest_lap": "NOR",
        "checo_position": "P5",
        "safety_cars": 1
    }
    mock_actual = {
        "pole": "LEC",
        "p1": "VER",
        "p2": "LEC",
        "p3": "NOR",
        "fastest_lap": "NOR",
        "checo_position": "P5",
        "safety_cars": 1
    }
    res = scorer.score_prediction(mock_prediction, mock_actual)
    print(f"Puntaje obtenido: {res['total_score']} / {res['max_possible']} ({res['accuracy_pct']}%)")
    print("Detalle de puntos por categoría:")
    for k, v in res["breakdown"].items():
        print(f"  - {k}: {v['points']} pts (Max: {v['max']}) | Predicho: {v['predicted']} vs Real: {v['actual']}")

def show_copilot_prompt():
    print("\n" + "="*70)
    print("🤖 PROMPT OFICIAL PARA GITHUB COPILOT (Para captura de entrega)")
    print("="*70)
    print(CopilotPromptGenerator.get_official_flyer_prompt())
    print("="*70)

def run_weather():
    from config.settings import PROCESSED_DATA_DIR
    from src.features.telemetry_analysis import TelemetryAnalyzer
    weather_file = PROCESSED_DATA_DIR / "weather_cdmx_weekend.json"
    if not weather_file.exists():
        from fetch_real_data import fetch_cdmx_weather
        fetch_cdmx_weather()

    with open(weather_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\n" + "="*70)
    print("🌤️ PRONÓSTICO METEOROLÓGICO REAL EN VIVO (CDMX - HERMANOS RODRÍGUEZ)")
    print("="*70)
    for d in data.get("days", []):
        impact = TelemetryAnalyzer.get_weather_degradation_impact(d["max_temp_c"], d["rain_prob_pct"])
        print(f"\n📅 Fecha: {d['date']}")
        print(f"   ▶ Temperatura Aire: {d['max_temp_c']}°C (Mín: {d['min_temp_c']}°C)")
        print(f"   ▶ Temperatura Estimada Asfalto: {impact['estimated_track_temp_c']}°C")
        print(f"   ▶ Probabilidad Lluvia: {d['rain_prob_pct']}% ({d['condition']})")
        print(f"   ▶ Viento Máximo: {d['wind_max_kmh']} km/h")
        print(f"   ▶ Estrategia Neumáticos: {impact['recommended_strategy']}")
        print(f"   ▶ Ventana Vuelta Rápida: {impact['fastest_lap_window']}")

def main():
    parser = argparse.ArgumentParser(description="Reto F1 - Estratega F1 con GitHub Stack")
    parser.add_argument("--predict", action="store_true", help="Ejecutar simulación y mostrar los 5 pronósticos")
    parser.add_argument("--physics", action="store_true", help="Mostrar análisis de física y degradación por altitud")
    parser.add_argument("--weather", action="store_true", help="Mostrar pronóstico del tiempo real en CDMX")
    parser.add_argument("--fetch-real", action="store_true", help="Descargar datos reales en vivo de APIs")
    parser.add_argument("--hybrid", action="store_true", help="Ejecutar predictor híbrido (Poisson, Regresión Múltiple, Random Forest)")
    parser.add_argument("--prompt", action="store_true", help="Mostrar el prompt para GitHub Copilot")
    parser.add_argument("--test-score", action="store_true", help="Demostración de cálculo de puntaje")
    parser.add_argument("--sims", type=int, default=2500, help="Número de iteraciones de Monte Carlo")
    parser.add_argument("--all", action="store_true", help="Ejecutar todas las acciones")

    args = parser.parse_args()

    print_banner()

    if args.fetch_real:
        import fetch_real_data
        fetch_real_data.main()
        return

    # Default to --predict if no flags provided
    if not any([args.predict, args.physics, args.weather, args.hybrid, args.prompt, args.test_score, args.all]):
        args.hybrid = True

    if args.weather or args.all:
        run_weather()

    if args.physics or args.all:
        run_physics()

    if args.hybrid or args.all:
        import f1_hybrid_predictor
        f1_hybrid_predictor.main()

    if args.predict:
        run_predictions(args.sims)

    if args.test_score or args.all:
        run_scoring_demo()

    if args.prompt or args.all:
        show_copilot_prompt()

if __name__ == "__main__":
    main()
