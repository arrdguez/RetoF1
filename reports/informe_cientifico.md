# Informe científico-estadístico de predicción

## Gran Premio de México 2026 — Desafío Tech "Estratega de F1"

**Evento objetivo:** Mexico City Grand Prix 2026 (ronda 19, 1 de noviembre de 2026), Autódromo Hermanos Rodríguez (2,240 m s. n. m.).
**Fecha de corte de datos:** 30–31 de octubre de 2026 (antes del inicio de la clasificación). Ningún dato posterior al corte fue utilizado.

---

## 1. Resumen ejecutivo

| # | Punto | Pronóstico | Probabilidad | Puntos |
|---|-------|-----------|-------------|--------|
| 1 | Pole (Q3) | **Antonelli (ANT)** | 15.1 % | 10 |
| 2 | Podio (1º·2º·3º) | **ANT → VER → HAM** | 0.7 % (conjunta) | 35 |
| 3 | Vuelta rápida | **Russell (RUS)** | 16.3 % | 10 |
| 4 | Posición de Checo Pérez | **P20** (o DNF) | 16.5 % | 15 |
| 5 | Safety Cars físicos | **0** | 47.2 % | 10 |

**Mensaje clave:** el campo 2026 está *muy apretado* en la cabeza (los 6 primeros pilotos tienen entre 11 % y 15 % de ganar), por lo que ninguna apuesta de podio tiene alta probabilidad. La certeza real del sistema está en dos extremos: **Checo en la cola (P17–P21 / DNF, por Cadillac con 0 puntos)** y **0 Safety Cars** como moda empírica.

---

## 2. Contexto temporal y coherencia

Se define explícitamente el evento y el corte para evitar contaminación (fugas de información futura):

- **Temporada:** 2026. **Evento:** GP de México (R19).
- **Corte:** 31 de octubre de 2026, antes de clasificación. La regla exige entregar antes de la qualy (transcripción del reto, línea 60).
- **Dato de forma reciente:** clasificación de pilotos y constructores tras la ronda 18 (COTA, 25 de octubre de 2026) — es la señal de ritmo más actual disponible y, al ser acumulada, resume la temporada completa, no solo 3–4 carreras.
- **Parrilla y equipos:** 22 pilotos / 11 equipos de 2026 (Mercedes, Ferrari, Red Bull, McLaren, Racing Bulls, Alpine, Haas, Audi, Williams, Aston Martin, Cadillac).

---

## 3. Datos y fuentes

| Conjunto | Fuente | Nota |
|----------|--------|------|
| Clasificación pilotos 2026 (R18) | Jolpica/Ergast (`api.jolpi.ca`) | 23 pilotos, puntos y victorias |
| Clasificación constructores 2026 (R18) | Jolpica/Ergast | 11 equipos |
| Histórico GP México (resultados + qualy) | Jolpica/Ergast, 2015–2025 | ganadores, podios, poles, vueltas rápidas, DNF, posiciones por piloto |
| Equipos 2026 por piloto | Wikipedia (tabla "Entries" 2026) | único dato de entrada manual, marcado y trazable |
| Safety Cars físicos por edición | Compilado de informes de carrera (2021–2024) | n = 4; ver limitaciones |
| Clima fin de semana 2026 | Open-Meteo | actual, no incorporado causalmente (ver §7) |

---

## 4. Metodología

### 4.1 Ratings de rendimiento (sustituyen ratings manuales)
Cada piloto recibe un *skill* logarítmico construido a partir de datos reales:

```
skill = 0.50·log(1+pts_2026)  +  0.35·log(1+pts_equipo_2026)  +  0.15·afinidad_México
```

- **Forma 2026 (50 %):** puntos reales del campeonato (escala log, que comprime diferencias extremas).
- **Equipo 2026 (35 %):** puntos del constructor (en F1 el coche explica gran parte del rendimiento).
- **Afinidad México (15 %):** log-odds construida con victorias, podios y posición media histórica de cada piloto en este trazado (2015–2025). Es un ajuste modesto, no dominante.

Los pesos (0.50 / 0.35 / 0.15) son hiperparámetros documentados, no calibrados hacia un resultado concreto.

### 4.2 Modelo Plackett-Luce (permutaciones)
La posición final es una **permutación**; el modelo correcto para ordenar es Plackett-Luce. La probabilidad de un orden completo es el producto de elecciones sucesivas con pesos proporcionales a `exp(skill)`. Esto produce la **probabilidad conjunta del podio exacto** (lo que exige el punto 2), no solo marginales.

### 4.3 Monte Carlo (incertidumbre y eventos raros)
Sobre el modelo base se añaden:
- **Ruido multiplicativo** (log-normal) por iteración: mayor en clasificación (σ=0.25) que en carrera (σ=0.15).
- **Abandonos mecánicos** por piloto: base 4 %, +3 % para Cadillac (escudería debutante), mezclado con el DNF-rate histórico de cada piloto en México.
- **Riesgo de curva 1** (recta de 890 m): 3 % en el pelotón medio (P4–P14), 1.2 % en cabeza/cola.
- **Penalización por salir atrás** en parrilla (el ganador sale, en promedio, de P1.8 según el histórico).

Se corren **20 000 iteraciones con semilla fija (42)** para reproducibilidad; el resultado se reporta como distribuciones completas, no como una sola cifra.

### 4.4 Poisson empírico para Safety Cars
El conteo de Safety Cars físicos se modela con Poisson de tasa empírica λ = 0.75 (3 SC en las 4 ediciones verificadas 2021–2024). La moda es **0 SC** (47.24 %), seguida de 1 SC (35.43 %). El pick de **máximo valor esperado** es 0 SC (4.72 puntos esperados frente a 3.54 de apostar por 1).

### 4.5 Vuelta rápida
Modelo honesto: combina ritmo de carrera proyectado (top 10) con el historial real de vuelta rápida en México. No se usa regresión sintética. Favorece a pilotos con ritmo y con historial de giro rápido en este circuito (Russell y Leclerc lideran con 2 vueltas rápidas cada uno en la era moderna).

### 4.6 Optimización de puntos esperados (EV)
La quiniela otorga **puntos parciales** (5 pts por piloto en el podio en posición distinta). Por tanto, el podio "más probable" no coincide necesariamente con el que maximiza puntos. Se optimiza la **terna ordenada de pilotos distintos** que maximiza el valor esperado:

```
EV = Σ_slots [ 5·P(piloto en podio) + (w_slot − 5)·P(piloto en posición exacta) ]
```
donde w = (15, 10, 10). La terna resultante (ANT→VER→HAM) es la de mayor valor esperado (≈ 9.1 pts).

---

## 5. Resultados detallados

### 5.1 Pole (moda)
| Piloto | Prob. |
|--------|-------|
| ANT | 15.1 % |
| HAM | 13.8 % |
| VER | 13.5 % |
| LEC | 12.8 % |
| RUS | 12.0 % |

La pole es una moneda al aire entre ~6 pilotos: refleja que 2026 no tiene un dominador absoluto en una vuelta.

### 5.2 Ganador (marginal)
| Piloto | Prob. |
|--------|-------|
| ANT | 14.9 % |
| VER | 14.7 % |
| HAM | 12.7 % |
| LEC | ~12 % |
| NOR | ~11 % |

Verstappen se mantiene competitivo por su dominio histórico en México (5 victorias, 6 podios en 10 salidas), pese a un Red Bull que en 2026 es 3º en constructores.

### 5.3 Posición de Checo Pérez
Distribución empírica (Cadillac, 0 puntos en 2026, 11º de 11 constructores):

| Resultado | Prob. |
|-----------|-------|
| P20 | 16.5 % |
| P19 | 15.6 % |
| DNF | 14.7 % |
| P18 | 11.3 % |
| P21 | 11.0 % |
| P17 | 7.4 % |

**La moda es P20, con un riesgo de DNF del 14.7 %.** Cualquier pronóstico de "P5–P7" carece de base en los datos de 2026.

### 5.4 Safety Cars físicos (Poisson, λ=0.75)
| k | Prob. |
|---|-------|
| 0 | 47.2 % |
| 1 | 35.4 % |
| 2 | 13.3 % |
| 3 | 3.3 % |

Moda y pick EV-óptimo: **0 Safety Cars**.

---

## 6. Validación y limitaciones (honestidad metodológica)

**Anclas de calibración observadas en el histórico de México (2015–2025):**
- La pole convierte en victoria el 50 % de las veces.
- El ganador sale, en promedio, de la posición 1.8.
- Verstappen concentra 5 de 10 victorias de la era moderna.

**Limitaciones:**
1. **Safety Cars:** la tasa λ=0.75 se estima con solo 4 ediciones verificadas; el intervalo de incertidumbre de λ con n=4 es amplio, por lo que "0" y "1" son casi equiprobables en la práctica. Es un prior débil, no una distribución validada.
2. **Sin telemetría por vuelta:** la vuelta rápida no usa degradación real (β1) porque FastF1 no aporta vueltas sin autenticación en este entorno; se usa ritmo + historial, explícitamente.
3. **Clima no causal:** el clima actual se presenta pero no altera la distribución (no hay datos de lluvia que justifiquen un cambio de λ o de DNF). Se documenta, no se fuerza.
4. **Sin backtest temporal completo:** la validación leave-one-out (predecir cada edición 2015–2025 con solo datos previos y puntuar con el sistema oficial) queda como siguiente paso. No se publican métricas de calibración que no se hayan calculado.
5. **Semilla fija:** los resultados son reproducibles (semilla 42); no se reportan intervalos multi-semilla en esta versión.

---

## 7. Respuestas finales para la quiniela

| # | Respuesta |
|---|-----------|
| 1 | Pole: **ANT (Antonelli)** |
| 2 | Podio: **1º ANT · 2º VER · 3º HAM** |
| 3 | Vuelta rápida: **RUS (Russell)** |
| 4 | Checo Pérez: **P20** |
| 5 | Safety Cars físicos: **0** |
