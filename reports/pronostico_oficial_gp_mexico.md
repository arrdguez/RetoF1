# Pronóstico oficial — GP de México 2026 (resumen ejecutivo)

**Evento:** Mexico City Grand Prix 2026 (R19, 1-nov-2026) · **Corte de datos:** 30-31 oct 2026.
Informe completo: [`informe_cientifico.md`](informe_cientifico.md) · Motor canónico: `python main.py --predict`.

## Quiniela (5 respuestas)

| # | Punto | Pronóstico | Prob. | Método estadístico | Puntos |
|---|-------|-----------|-------|--------------------|--------|
| 1 | Pole (Q3) | **ANT — Antonelli** | 15.2 % | Plackett-Luce + Monte Carlo | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · HAM · VER** | 0.4 % conjunta | Plackett-Luce + optimización EV | 35 |
| 3 | Vuelta rápida | **RUS — Russell** | 14.9 % | Pesos ritmo × historial | 10 |
| 4 | Checo Pérez | **P20** (DNF 15.5 %) | 15.9 % | Distribución empírica Monte Carlo | 15 |
| 5 | Safety Cars físicos | **0** | 48.2 % | Poisson-Gamma Bayesiano | 10 |

## Justificación breve

- **Pole y podio:** campo muy apretado (ANT, VER, HAM, RUS, NOR entre 10 % y 16 % de ganar). Antonelli lidera por forma 2026 (365 pts, 9 victorias); Verstappen compensa con su dominio histórico en México (5 victorias). La terna ANT→HAM→VER maximiza el valor esperado del podio (8.4 pts).
- **Vuelta rápida:** Russell (2 giros rápidos históricos en México) + ritmo 2026.
- **Checo:** Cadillac tiene 0 puntos en 2026 (11º de 11); la moda es P20, con 15.5 % de DNF.
- **Safety Cars:** Poisson-Gamma Bayesiano (3 SC en 4 ediciones) → moda **0 SC** (48.2 %), λ posterior media 0.80 (IC 90 % [0.27, 1.55]).

## Metodología (resumen)

Ratings 2026 (35 % forma + 20 % victorias + 30 % equipo + 15 % afinidad México) → Plackett-Luce (permutaciones) → Monte Carlo 20 000 iteraciones (DNF, curva 1, parrilla) → Poisson-Gamma Bayesiano (SC) → optimización de puntos esperados (EV).

**Regla clave del concurso:** si aciertas al piloto en el podio pero no su posición exacta, ganas **5 pts** (premio parcial). Por eso se optimiza la terna completa, no el podio "más probable".

Sin valores a mano, sin regresión sintética, sin Random Forest sobre muestras diminutas. Cada cifra se calcula en `src/models/statistical_engine.py`.
