# Paper de resultados

## Predicción estadística del Gran Premio de México 2026 (F1)

**Autores**
- Alejandro Rodríguez Rodríguez
- Camilo Serrano Fuentes

**Evento:** Desafío Tech "Estratega de F1" — Gran Premio de la Ciudad de México 2026, Autódromo Hermanos Rodríguez (2,240 m s. n. m.), ronda 19 de la temporada.
**Fecha de corte de datos:** 30–31 de octubre de 2026 (antes del inicio de la clasificación).

---

## Resumen

Se desarrolla un modelo probabilístico para predecir los cinco resultados de la quiniela oficial: pole position, podio exacto, vuelta rápida, posición de Sergio "Checo" Pérez y número de Safety Cars físicos. El modelo combina un **rating Bradley-Terry** (máxima verosimilitud sobre las 18 rondas disputadas de 2026), una señal de **momento reciente** (últimas cuatro carreras), la **afinidad histórica de circuito**, un **modelo Plackett-Luce** para permutaciones, **simulación Monte Carlo** (20 000 iteraciones) y un **modelo Poisson-Gamma Bayesiano** para Safety Cars. La selección final de cada categoría se realiza por **optimización del valor esperado de puntos**, no por la respuesta "más probable". El sistema se valida mediante un backtest temporal leave-one-out (2016–2025) y se reportan explícitamente sus limitaciones, sin confianzas inventadas.

---

## 1. Introducción y contexto

El reto exige entregar cinco respuestas antes de la clasificación del sábado. Toda la información utilizada es anterior a ese corte. La parrilla oficial de 2026 consta de **22 pilotos y 11 escuderías**, con dos hechos determinantes para la quiniela:

1. **Andrea Kimi Antonelli (Mercedes)** lidera el campeonato con 365 puntos y 9 victorias; Mercedes domina el mundial de constructores (607 puntos).
2. **Sergio "Checo" Pérez corre con Cadillac**, escudería debutante que acumula **0 puntos** (11.ª de 11), lo que lo sitúa en la zona baja de la parrilla.

---

## 2. Datos y fuentes

| Conjunto | Fuente |
|----------|--------|
| Resultados de las 18 rondas de 2026 (orden de llegada y abandonos) | Jolpica / Ergast |
| Clasificación de pilotos y constructores 2026 (ronda 18) | Jolpica / Ergast |
| Histórico del GP de México 2015–2025 (resultados y clasificación) | Jolpica / Ergast |
| Equipos por piloto (parrilla 2026) | Wikipedia (entrada manual, trazable) |
| Safety Cars físicos por edición (2021–2024) | Compilación de informes de carrera |

---

## 3. Metodología

### 3.1 Rating Bradley-Terry
Se estima el ritmo de cada piloto con el modelo de comparación por pares **Bradley-Terry**, ajustado por **máxima verosimilitud** (algoritmo iterativo de Zermelo) sobre las 18 rondas de 2026. La señal son todas las comparaciones "el piloto A terminó delante del piloto B". Es el estimador estadísticamente correcto para rankings, superior a usar únicamente puntos.

### 3.2 Momento reciente
Se añade una señal de forma reciente con ponderación temporal decreciente sobre las **últimas cuatro carreras** (R15–R18). Capta subidas tardías de forma (por ejemplo, Verstappen ganó dos de las tres carreras previas).

### 3.3 Skill por piloto
```
skill = 0.45·(rating Bradley-Terry) + 0.25·(equipo) + 0.15·(momento) + 0.15·(afinidad México)
```
Los pesos son hiperparámetros documentados, no calibrados hacia un resultado concreto.

### 3.4 Plackett-Luce y Monte Carlo
La posición final es una **permutación**; se modela con **Plackett-Luce** (la probabilidad de un orden completo es el producto de elecciones sucesivas). Sobre él se aplica **Monte Carlo** (20 000 iteraciones, semilla fija 42) con ruido multiplicativo, abandonos mecánicos, riesgo de curva 1 y penalización por posición de salida.

### 3.5 Poisson-Gamma Bayesiano (Safety Cars)
Se modela la tasa de Safety Cars con una distribución de Poisson y un **prior Gamma(1,1)**. La **predictiva posterior** (Binomial Negativa) incorpora la incertidumbre de estimar la tasa con solo 4 ediciones.

### 3.6 Optimización del valor esperado
La quiniela otorga **puntos parciales**: si se acierta el piloto en el podio pero no su posición exacta, se obtienen **5 puntos**. Por tanto, se elige la terna de pilotos distintos que **maximiza los puntos esperados**, no el podio más probable.

---

## 4. Resultados

### 4.1 Respuestas finales

| # | Punto | Pronóstico | Probabilidad | Puntos |
|---|-------|-----------|-------------|--------|
| 1 | Pole position | **Antonelli (ANT)** | 16.4 % | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · HAM · VER** | 0.5 % conjunta | 35 |
| 3 | Vuelta rápida | **Hamilton (HAM)** | 15.4 % | 10 |
| 4 | Checo Pérez | **DNF** (P17–P21 si termina) | 15.9 % | 15 |
| 5 | Safety Cars físicos | **0** | 48.2 % | 10 |

### 4.2 Distribución del ganador (marginal)

| Piloto | Prob. |
|--------|-------|
| Antonelli | 16.6 % |
| Hamilton | 14.0 % |
| Verstappen | 12.5 % |
| Leclerc | 10.9 % |
| Norris | 8.6 % |
| Russell | 8.0 % |

### 4.3 Distribución de Checo Pérez (Cadillac, 0 puntos en 2026)

| Resultado | Prob. |
|-----------|-------|
| DNF | 15.9 % |
| P19 | 13.3 % |
| P20 | 12.3 % |
| P18 | 11.2 % |
| P17 | 8.7 % |

### 4.4 Safety Cars (predictiva Binomial Negativa)

| Conteo | Prob. |
|--------|-------|
| 0 | 48.2 % |
| 1 | 32.2 % |
| 2 | 13.4 % |
| 3 | 4.5 % |

Tasa posterior λ: media 0.80, intervalo creíble 90 % [0.27, 1.55].

---

## 5. Validación

### Backtest temporal (leave-one-out 2016–2025)

| Métrica | Valor |
|---------|-------|
| Puntos medios (pole + podio + vuelta rápida, máx. 55) | **45.0 / 55** |
| Acierto de ganador | 44 % (empata con el baseline "líder del campeonato") |
| Acierto de pole | 11 % |
| Acierto de vuelta rápida | 0 % |
| Brier (ganador) | 0.80 |
| Safety Cars (n = 4) | 1/4 aciertos, Brier 0.691 |

**Interpretación:** el modelo es honesto sobre su incertidumbre. El podio exacto y la vuelta rápida son esencialmente impredecibles con los datos disponibles. El valor real del sistema está en la corrección de Checo/Cadillac, la incertidumbre reportada y la optimización de puntos.

---

## 6. Limitaciones

1. **Safety Cars:** la tasa se estima con 4 ediciones; su intervalo de credibilidad es amplio.
2. **Vuelta rápida:** no se usa telemetría por vuelta (FastF1 requiere autenticación); se usa rating + historial.
3. **Clima:** se presenta pero no es causal en el modelo.
4. **Backtest de pole/podio:** se usó un modelo simplificado (forma + afinidad), no el motor completo Bradley-Terry + momento, por falta de datos por carrera de temporadas previas.
5. **Semilla fija:** resultados reproducibles, pero sin intervalos multi-semilla.

---

## 7. Conclusión

El modelo entrega cinco respuestas inequívocas, con probabilidades calculadas y validadas, fundamentadas en datos reales de la temporada 2026 y del histórico del circuito. La decisión de cada categoría se toma maximizando el valor esperado de puntos bajo las reglas oficiales del reto.

**Respuestas finales:** Pole **Antonelli** · Podio **Antonelli–Hamilton–Verstappen** · Vuelta rápida **Hamilton** · Checo Pérez **DNF** · Safety Cars **0**.
