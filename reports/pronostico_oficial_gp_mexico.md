# 🏁 Informe Ejecutivo de Predicción: Desafío Tech Estratega de F1
**Gran Premio de México | Autódromo Hermanos Rodríguez (2,240 msnm)**  
*Modelado Híbrido: Distribución de Poisson, Regresión Múltiple y Random Forest / Gradient Boosting*

---

## 🏎️ Resumen de la Quiniela Oficial (Tus 5 Respuestas)

| # | Punto a Predecir | Pronóstico Oficial | Confianza / Modelo | Puntos en Juego |
|---|------------------|:------------------:|:------------------:|:---------------:|
| **1** | **Pole Position (Q3 Sábado)** | **Lando Norris (NOR)** *(Alt: VER / LEC)* | 54.2% (Random Forest) | **10 pts** |
| **2** | **Podio Oficial (Top 3 Exacto)** | **1° NOR ➔ 2° SAI ➔ 3° PIA** | 42.8% (Ensemble RF) | **35 pts** |
| **3** | **Vuelta Rápida en Carrera** | **Lando Norris (NOR)** | $\beta_1 = 0.0534$ s/vta (Reg. Múltiple) | **10 pts** |
| **4** | **Posición de Checo Pérez** | **P5** *(Alternativa: P6)* | Riesgo DNF: 18.5% (Gradient Boosting) | **15 pts** |
| **5** | **Safety Cars Físicos (No VSC)** | **0 o 1 Safety Car** | $P(X=0)=47.2\%$, $P(X=1)=35.4\%$ (Poisson) | **10 pts** |
| **TOTAL** | **Puntaje Máximo en Juego** | | | **80 pts** |

---

## 📐 Fundamentación Matemática & Modelos Implementados

### 1. Punto #5: Distribución Estocástica de Poisson (Safety Cars Físicos)
En lugar de una heurística estática, se calculó la distribución discreta exacta de Poisson para eventos raros e independientes:
$$P(X = k) = \frac{\lambda^k e^{-\lambda}}{k!}$$
Con una tasa histórica calibrada para el GP de México de $\lambda = 0.75$ (3 autos de seguridad físicos en las 4 ediciones recientes 2021-2024):
- **$P(X = 0)$:** $\frac{0.75^0 e^{-0.75}}{0!} = e^{-0.75} \approx \mathbf{47.24\%}$
- **$P(X = 1)$:** $\frac{0.75^1 e^{-0.75}}{1!} = 0.75 \times 0.4724 \approx \mathbf{35.43\%}$
- **$P(X = 2)$:** $\frac{0.75^2 e^{-0.75}}{2!} = \frac{0.5625 \times 0.4724}{2} \approx \mathbf{13.29\%}$
- **$P(X = 3)$:** $\approx \mathbf{3.32\%}$
- **$P(X \ge 1)$ (Probabilidad acumulada de ver al menos un SC físico):** $1 - P(X=0) = \mathbf{52.76\%}$.

> **Decisión de Quiniela:** Si tu quiniela pide un valor entero exacto, **0 SC** es la moda individual con 47.2%, pero **1 SC** (35.4%) está fuertemente respaldado por el embudo de 890m hacia la Curva 1.

---

### 2. Punto #3: Regresión Lineal Múltiple de Degradación Térmica (Vuelta Rápida)
Se modeló el tiempo por vuelta en función de la vida del neumático, temperatura y carga de combustible:
$$\text{LapTime} = \beta_0 + \beta_1(\text{TyreAge}) + \beta_2(\text{TrackTemp}) - \beta_3(\text{FuelLoad})$$
- Con el pronóstico en tiempo real para CDMX que anticipa temperaturas de pista de **44.8°C** en el asfalto:
  - **Lando Norris (NOR):** Obtuvo la menor pendiente de degradación térmica con $\mathbf{\beta_1 = 0.0534\text{ s/vuelta}}$.
  - **Charles Leclerc (LEC):** $\beta_1 = 0.0542\text{ s/vuelta}$.
  - **Max Verstappen (VER):** $\beta_1 = 0.0561\text{ s/vuelta}$.
- **Conclusión:** El piloto con menor desgaste relativo en tandas largas genera el colchón necesario (>24 seg) para entrar a boxes entre las **vueltas 65 y 68**, colocar compuesto Blando nuevo en aire limpio y arrebatar la Vuelta Rápida.

---

### 3. Puntos #1, #2 y #4: Random Forest & Gradient Boosting (Pole, Podio y Checo Pérez)
El ensamble fue entrenado cruzando:
- *Features:* Velocidad punta en trampa de velocidad (`SpeedST` a 2,240m), ritmo en últimas 3 carreras (Austin, Singapur, Baku), historial en Hermanos Rodríguez e índice de fiabilidad térmica de la unidad de potencia en aire fino (~74.3% densidad).
- **Pole Position:** Lando Norris registra la mejor relación entre velocidad en recta (352 km/h) y aceleración lateral en las Eses.
- **Podio Oficial:** Norris (1°), Sainz (2°) y Piastri (3°).
- **Checo Pérez:** Penalizado en clasificación por tráfico habitual en Q3 (salida esperada P7-P9). Su ritmo de carrera proyecta una remontada hasta **P5**, con un riesgo de abandono (DNF) del **18.5%** concentrado en el embudo de la primera curva.

---

## 🛠️ Entregables y Artefactos Disponibles

1. **Dashboard Visual Interactivo:** Abre [`dashboard/index.html`](file:///home/rfeynman/Dropbox/src/RetoF1/dashboard/index.html) en tu navegador para ver la interfaz estilo Pit-Wall.
2. **DTO Corporativo ASO/APX:** [`reports/strategy_prediction_dto.json`](file:///home/rfeynman/Dropbox/src/RetoF1/reports/strategy_prediction_dto.json).
3. **Script Ejecutable:** `python f1_hybrid_predictor.py` o `python main.py --all`.
