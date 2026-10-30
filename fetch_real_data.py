#!/usr/bin/env python3
"""
fetch_real_data.py
Consumes real-time and official historical data for the Mexico GP challenge:
1. Live track weather for Mexico City (Autódromo Hermanos Rodríguez) for this weekend.
2. Official results and qualifying of the last 3 races (Baku, Marina Bay, COTA) via FastF1/Ergast.
3. Official Mexico GP historical editions (2021, 2022, 2023, 2024) and Checo Pérez performance.
"""

import json
import logging
from pathlib import Path
import requests
import pandas as pd

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.apis.fastf1_client import FastF1Client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def fetch_cdmx_weather() -> dict:
    """
    Fetches real-time weather and 4-day forecast for Autódromo Hermanos Rodríguez (2,240m).
    """
    logger.info("📡 Obteniendo pronóstico meteorológico en vivo para CDMX (Autódromo Hermanos Rodríguez)...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 19.4042,
        "longitude": -99.0907,
        "elevation": 2240,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,windspeed_10m_max,weathercode",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,surface_pressure,windspeed_10m",
        "timezone": "America/Mexico_City",
        "forecast_days": 4
    }
    res = requests.get(url, params=params, timeout=10)
    data = res.json()

    # Build structured summary for the weekend
    daily = data.get("daily", {})
    weather_summary = {
        "circuit": "Autódromo Hermanos Rodríguez",
        "coordinates": {"lat": 19.4042, "lon": -99.0907, "elevation_m": 2240},
        "days": []
    }

    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rain_probs = daily.get("precipitation_probability_max", [])
    wind_speeds = daily.get("windspeed_10m_max", [])

    for i in range(len(dates)):
        weather_summary["days"].append({
            "date": dates[i],
            "max_temp_c": max_temps[i],
            "min_temp_c": min_temps[i],
            "rain_prob_pct": rain_probs[i],
            "wind_max_kmh": wind_speeds[i],
            "condition": "Seco / Caluroso" if rain_probs[i] < 20 else "Riesgo de Lluvia"
        })

    # Save to raw and processed
    raw_path = RAW_DATA_DIR / "weather_cdmx_live.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    processed_path = PROCESSED_DATA_DIR / "weather_cdmx_weekend.json"
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(weather_summary, f, indent=2)

    logger.info("✅ Clima guardado exitosamente en %s", processed_path)
    return weather_summary

def fetch_last_3_races(fastf1_client: FastF1Client) -> dict:
    """
    Fetches real official results for the last 3 races (R17 Baku, R18 Singapore, R19 COTA).
    """
    logger.info("📡 Obteniendo resultados reales de las últimas 3 carreras de la temporada...")
    last_races_info = []
    rounds = [
        (17, "Azerbaijan Grand Prix (Baku)"),
        (18, "Singapore Grand Prix (Marina Bay)"),
        (19, "United States Grand Prix (COTA)")
    ]

    for round_num, name in rounds:
        df_race = fastf1_client.get_race_results(2024, round_num)
        df_quali = fastf1_client.get_qualifying_results(2024, round_num)

        race_entry = {
            "round": round_num,
            "name": name,
            "pole": None,
            "winner": None,
            "podium": [],
            "checo_finish": None,
            "checo_status": None
        }

        if df_quali is not None and not df_quali.empty:
            race_entry["pole"] = df_quali.iloc[0]["driverCode"]

        if df_race is not None and not df_race.empty:
            race_entry["winner"] = df_race.iloc[0]["driverCode"]
            race_entry["podium"] = df_race.head(3)["driverCode"].tolist()
            checo_row = df_race[df_race["driverCode"] == "PER"]
            if not checo_row.empty:
                race_entry["checo_finish"] = int(checo_row.iloc[0]["position"])
                race_entry["checo_status"] = checo_row.iloc[0]["status"]

        last_races_info.append(race_entry)

    processed_path = PROCESSED_DATA_DIR / "last_3_races_real.json"
    payload = {"season": 2024, "races": last_races_info}
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info("✅ Últimas 3 carreras guardadas en %s", processed_path)
    return payload

def fetch_mexico_gp_historical(fastf1_client: FastF1Client) -> dict:
    """
    Fetches historical Mexico GP results from FastF1 / Ergast (2021-2024).
    """
    logger.info("📡 Obteniendo histórico oficial del GP de México (2021-2024)...")
    history = []
    years = [2021, 2022, 2023, 2024]

    for yr in years:
        sched = fastf1_client.ergast.get_race_schedule(season=yr)
        if sched is not None and not sched.empty:
            mex = sched[sched["raceName"].str.contains("Mexico", case=False, na=False)]
            if not mex.empty:
                rnd = int(mex.iloc[0]["round"])
                df_res = fastf1_client.get_race_results(yr, rnd)
                df_q = fastf1_client.get_qualifying_results(yr, rnd)

                pole = df_q.iloc[0]["driverCode"] if df_q is not None and not df_q.empty else "N/A"
                winner = df_res.iloc[0]["driverCode"] if df_res is not None and not df_res.empty else "N/A"
                podium = df_res.head(3)["driverCode"].tolist() if df_res is not None and not df_res.empty else []
                checo_row = df_res[df_res["driverCode"] == "PER"] if df_res is not None else pd.DataFrame()
                checo_pos = int(checo_row.iloc[0]["position"]) if not checo_row.empty else "DNF"

                history.append({
                    "year": yr,
                    "round": rnd,
                    "pole": pole,
                    "winner": winner,
                    "podium": podium,
                    "checo_finish": checo_pos
                })

    processed_path = PROCESSED_DATA_DIR / "mexico_gp_historical_real.json"
    payload = {"circuit": "Autódromo Hermanos Rodríguez", "editions": history}
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info("✅ Histórico del GP de México guardado en %s", processed_path)
    return payload

def main():
    logger.info("🏁 Iniciando extracción de datos reales de APIs...")
    f1_client = FastF1Client()
    
    weather = fetch_cdmx_weather()
    print("\n--- PRONÓSTICO FIN DE SEMANA CDMX ---")
    for d in weather["days"]:
        print(f"📅 {d['date']}: Max {d['max_temp_c']}°C | Min {d['min_temp_c']}°C | Lluvia: {d['rain_prob_pct']}% | Viento: {d['wind_max_kmh']} km/h ({d['condition']})")

    races = fetch_last_3_races(f1_client)
    print("\n--- ÚLTIMAS 3 CARRERAS (DATOS REALES) ---")
    for r in races["races"]:
        print(f"🏁 {r['name']}: Pole={r['pole']}, Ganador={r['winner']}, Podio={r['podium']}, Checo=P{r['checo_finish']} ({r['checo_status']})")

    history = fetch_mexico_gp_historical(f1_client)
    print("\n--- HISTÓRICO GP DE MÉXICO (2021-2024) ---")
    for h in history["editions"]:
        print(f"🇲🇽 {h['year']}: Pole={h['pole']}, Ganador={h['winner']}, Podio={h['podium']}, Checo=P{h['checo_finish']}")

if __name__ == "__main__":
    main()
