# Ficha de decisión, perfil CCPC y frontera — Track 2

Fuente: mensaje del usuario «ahora aplica esto» (1 ficha «¿Por qué este municipio?», 2 perfil demográfico separado del predictor, 3 incertidumbre de ranking, 4 Modo Director, frontera de decisión). Autorización: cambios locales, repositorio privado.

## Diseño y límites

- La ficha explica la decisión existente; no reentrena ni cambia alpha, cortes ni selección.
- Perfil CCPC por edad/sexo/tipo de sección calculado directo de los seis ZIP; se agrega como **capa explicativa posterior** y nunca alimenta a Ridge, a la referencia ni a la prioridad.
- Incertidumbre de ranking con la frecuencia entre las seis variantes (2 métodos × NS 5/10/20), no con el rango ±21.05 pp. El rango histórico se conserva solo en una nota técnica colapsada.
- Modo Director: capacidad territorial (municipios) o humana (personas alcanzables), confianza mínima y plan sugerido.
- Frontera de decisión: núcleo robusto 6/6, zona de revisión 1/6–5/6 y fuera. El piloto se propone sobre la frontera.
- Sin causalidad, sin probabilidad calibrada, sin inventar costos ni correspondencia distrital.

## Tareas

- [x] Lógica pura: `confidenceTier`, `planByBudget`, `decisionFrontier` y membresía por variante en `decision.js`, con pruebas Node.
- [x] Datos: `modelado/perfil_demografico.py` (edad/sexo/sección, 2021 y 2024) e incrustación en la demo.
- [x] Ficha «¿Por qué este municipio?» con razones, robustez, acuerdo de métodos, acción, hipótesis y evaluación.
- [x] Confianza de prioridad y acuerdo de métodos; ±21.05 pp fuera de la vista principal.
- [x] Modo Director con capacidad dual, confianza mínima y resumen de plan.
- [x] Frontera de decisión y propuesta de piloto sobre la frontera.
- [x] Verificación: pruebas Node ampliadas y 24 comprobaciones de navegador.
- [x] Documentación vigente, commit y push.

## Ejecución y evidencia (2026-10-05)

- `modelado/perfil_demografico.py`: 2,477 municipios, 2021 y 2024, 2.1 MB. Reconciliación: la suma de `n` por dimensión coincide con SV+NV de la base municipal-año (comprobado en Aguascalientes 01001, 712,269).
- Pruebas Node: 12 en verde (`decision.test.cjs`), incluidas confianza, capacidad humana, frontera y membresía.
- Navegador Edge: 24/24 comprobaciones (`verificar_demo.py`), incluidas ficha, plan sugerido, frontera, perfil CCPC, capacidad humana y confianza mínima; sin errores de página; apertura `file://`.
- Perfil nacional 2024 coherente con patrones documentados por el INE: mayor abstención entre jóvenes 18–29 (≈51%) que entre 60+ (≈29%) y entre hombres que entre mujeres.
- Límites explícitos: el perfil describe composición agregada y abstención por grupo; no es un perfil individual ni un efecto. Confianza = frecuencia entre seis variantes, no probabilidad. El rango ±21.05 pp sigue siendo error histórico, no intervalo prospectivo.
