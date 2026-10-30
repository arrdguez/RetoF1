# Pronóstico oficial — GP de México 2026 (resumen ejecutivo)

**Evento:** Mexico City Grand Prix 2026 (R19, 1-nov-2026) · **Corte de datos:** 30-31 oct 2026.
Informe completo: [`informe_cientifico.md`](informe_cientifico.md) · Motor canónico: `python main.py --predict`.

## Quiniela (5 respuestas)

| # | Punto | Pronóstico | Prob. | Puntos |
|---|-------|-----------|-------|--------|
| 1 | Pole (Q3) | **ANT — Antonelli** | 15.1 % | 10 |
| 2 | Podio (1º·2º·3º) | **ANT · VER · HAM** | 0.7 % conjunta | 35 |
| 3 | Vuelta rápida | **RUS — Russell** | 16.3 % | 10 |
| 4 | Checo Pérez | **P20** (DNF 14.7 %) | 16.5 % | 15 |
| 5 | Safety Cars físicos | **0** | 47.2 % | 10 |

## Justificación breve

- **Pole y podio:** campo muy apretado (ANT, VER, HAM, LEC, RUS, NOR entre 11 % y 15 % de ganar). Antonelli lidera por forma 2026 (365 pts, 9 victorias); Verstappen compensa con su dominio histórico en México (5 victorias). La terna ANT→VER→HAM maximiza el valor esperado del podio.
- **Vuelta rápida:** Russell (2 giros rápidos históricos en México) + ritmo 2026.
- **Checo:** Cadillac tiene 0 puntos en 2026 (11º de 11); la moda es P20, con 14.7 % de DNF.
- **Safety Cars:** Poisson empírico λ=0.75 (3 SC en 4 ediciones 2021-2024) → moda **0 SC**.

## Metodología (resumen)

Ratings 2026 (50 % forma + 35 % equipo + 15 % afinidad México) → Plackett-Luce (permutaciones) → Monte Carlo 20 000 iteraciones (DNF, curva 1, parrilla) → Poisson empírico (SC) → optimización de puntos esperados (EV).

Sin valores a mano, sin regresión sintética, sin Random Forest sobre muestras diminutas. Cada cifra se calcula en `src/models/statistical_engine.py`.
