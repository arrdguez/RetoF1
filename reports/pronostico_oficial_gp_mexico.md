# 🏁 Informe Ejecutivo de Predicción Canónica: Desafío Tech Estratega de F1
**Gran Premio de México | Autódromo Hermanos Rodríguez (2,240 msnm)**  
*Pipeline Canónico Unificado: Simulación Monte Carlo + Poisson Estocástico + Telemetría Real*

---

## 🏎️ Quiniela Oficial Unificada (Tus 5 Respuestas Definitivas)

| # | Punto a Predecir | Pronóstico Oficial | Probabilidad / Modelo | Puntos en Juego |
|---|------------------|:------------------:|:--------------------:|:---------------:|
| **1** | **Pole Position (Q3 Sábado)** | **Charles Leclerc (LEC)** | **61.04%** (Monte Carlo Pace) | **10 pts** |
| **2** | **Podio Oficial (Top 3 Exacto)** | **1° VER ➔ 2° LEC ➔ 3° NOR** | **32.72%** (P. Conjunta Monte Carlo) | **35 pts** |
| **3** | **Vuelta Rápida en Carrera** | **Lando Norris (NOR)** | **36.12%** (Ventana Táctica de Pits) | **10 pts** |
| **4** | **Posición de Checo Pérez** | **P7** *(Rango P6-P8)* | **30.56%** (Empírica MC; DNF: 6.6%) | **15 pts** |
| **5** | **Safety Cars Físicos (No VSC)** | **1 Safety Car** | **36.74%** (Poisson $\lambda_{\text{eff}} = 1.05$) | **10 pts** |
| **TOTAL** | **Puntaje Máximo en Juego** | | | **80 pts** |

---

## 📐 Fundamentación Matemática & Modelos

### 1. Punto #5: Distribución Estocástica de Poisson (Safety Cars Físicos)
$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$
- **Tasa Histórica Base en CDMX ($\lambda_{\text{base}} = 0.75$):** 3 autos de seguridad físicos en las 4 carreras recientes (2021, 2023, 2024). Con esta tasa base, la moda discreta pura es $k=0$ (47.24%) y $k=1$ (35.43%).
- **Tasa Operativa Ajustada ($\lambda_{\text{eff}} = 1.05$):** Incorporando la frenada de 355 km/h a 90 km/h en la Curva 1 (la recta de salida más larga de la F1 con 890m) y las fallas de refrigeración de frenos por baja densidad del aire (2,240m):
  - **$P(X = 0)$:** **34.99%**
  - **$P(X = 1)$:** **36.74% (Moda Estadística)**
  - **$P(X = 2)$:** **19.29%**
  - **$P(X = 3)$:** **6.75%**
  - **$P(X \ge 1)$ (Probabilidad acumulada de al menos un SC físico):** **65.01%**.

---

### 2. Punto #3: Modelo Táctico de Vuelta Rápida y Ventana de Pits
En la F1 moderna, la Vuelta Rápida la logra el piloto del Top 4 que disponga de una **brecha libre superior a 24 segundos** sobre su perseguidor entre las **vueltas 65 y 68** para realizar una parada en boxes sin perder su lugar en el podio.
- **Lando Norris (NOR)** y **Max Verstappen (VER)** son los candidatos principales con gaps suficientes en tandas largas para montar neumáticos Blandos nuevos.
- Con **36.12% de probabilidad táctica**, Norris encabeza la proyección de vuelta rápida.

---

### 3. Puntos #1, #2 y #4: Simulación Monte Carlo (2,500 Carreras)
- **Pole Position (Q3):** Charles Leclerc (LEC, 61.0%) supera a Verstappen (38.1%) en simulación de clasificación a una vuelta debido a la tracción de Ferrari en las curvas lentas del Sector 3 (Foro Sol).
- **Podio Oficial (Carrera 71 Vueltas):** Max Verstappen (VER, 50.1%) capitaliza la velocidad punta de Red Bull en recta y su historial dominante en México (5 victorias) para llevarse el triunfo, escoltado por Leclerc (2°) y Norris (3°).
- **Checo Pérez:** La simulación Monte Carlo completa arroja una distribución realista:
  - **P7:** **30.56%**
  - **P6:** **28.20%**
  - **P8:** **24.00%**
  - **P5:** **7.00%**
  - **DNF:** **6.64%** (riesgo de contacto en Curva 1 o sobrecalentamiento).

---

## 🛠️ Archivos Actualizados
- **CLI Principal:** `./venv/bin/python3 main.py --predict`
- **Predictor Híbrido:** `./venv/bin/python3 f1_hybrid_predictor.py`
- **Dashboard Web:** [`dashboard/index.html`](file:///home/rfeynman/Dropbox/src/RetoF1/dashboard/index.html)
- **JSON DTO ASO/APX:** [`reports/strategy_prediction_dto.json`](file:///home/rfeynman/Dropbox/src/RetoF1/reports/strategy_prediction_dto.json)
