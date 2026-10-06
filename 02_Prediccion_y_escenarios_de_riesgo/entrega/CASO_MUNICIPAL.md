# Caso municipal: de una prioridad a una propuesta revisable

6 de octubre de 2026. Caso 23008, **SOLIDARIDAD**, Quintana Roo: nombre del catálogo histórico utilizado, no certificación de denominación o límites actuales.

## Configuración reproducible

Abrir `demo/index.html`. Todas las entidades, búsqueda vacía, filtro de catálogo constante activado, Ridge, tasa, capacidad de 50 municipios, estabilidad «Todas», alcance 1,000 y respuesta supuesta 25%. Buscar el caso en la lista y abrir su ficha. No introducirlo en el buscador antes de revisar el puesto: la búsqueda cambia el universo y la estabilidad.

## Evidencia del caso

| Variable | Valor | Significado |
|---|---:|---|
| Puesto Ridge | 1 de 1,144 estimables | Con la configuración indicada |
| Puesto de referencia | 3 | Misma cohorte y criterio |
| Abstención 2021 | 66.30% | Última intermedia observada |
| Abstención 2024 | 48.96% | Presidencial observada; otro tipo electoral |
| Estimación exploratoria 2027 | 62.11% | Ridge, no tasa validada |
| NS 2021 / 2024 | 9.60% / 2.28% | Calidad de antecedentes |
| SV+NV 2024 | 255,362 | Base observable histórica |
| LN 2024 | 261,323 | Incluye NS; no denominador del escenario |
| Composición 18–29 / urbana | 28.26% / 91.02% | Proporciones agregadas de LN |
| Estabilidad | 4/6, media | Seleccionado en las cuatro variantes elegibles |

Referencia y Ridge coinciden dentro de la capacidad. Las variantes NS ≤5% no son elegibles por NS 2021. Por eso pertenece a la zona de revisión, aunque ocupe el primer lugar Ridge. Cuatro variantes de seis no equivalen a una probabilidad de acierto del 67%. Catálogo constante tampoco acredita fronteras constantes.

## Propuesta operativa por validar

- **Acción:** talleres abiertos sobre requisitos, ubicación de casilla y procedimiento electoral en espacios educativos y comunitarios. La composición joven orienta la exploración de canales; no demuestra desinterés ni barreras.
- **Responsable propuesto:** área de educación cívica y junta local, con enlace territorial; confirmar atribuciones y disponibilidad antes de ejecutar.
- **Cobertura propuesta:** 1,000 personas alcanzadas, atención voluntaria y abierta. No es una capacidad institucional confirmada.
- **Condiciones:** verificar sedes, accesibilidad, calendario, pertinencia de materiales, límites territoriales y capacidad. Registrar asistencia única de forma agregada, sin identidades en la demo.
- **Recursos:** personas alcanzadas, sesiones realizadas y horas de facilitación registradas. Presupuesto monetario y número de sesiones por acordar con el área usuaria.
- **Hipótesis:** información clara podría reducir barreras de conocimiento. El modelo no identifica esa causa ni prueba el efecto.
- **Medición inmediata:** alcance único agregado, cumplimiento de actividades y cambio de conocimiento mediante instrumento previo/posterior definido antes de iniciar. Documentar pérdidas y sesgo de participación voluntaria.
- **Evaluación de participación:** protocolo piloto independiente, con asignación aleatoria por unidad territorial elegible, balance, tamaño de muestra/potencia y análisis predefinidos. Comparar participación agregada en la siguiente elección comparable, si es medible y autorizado. No atribuir causalidad a un antes/después de este municipio.

## Escenario hipotético

Con alcance de 1,000 y respuesta supuesta de 25%:

```text
H = 1,000 × 0.6210680555 × 0.25 = 155.27 adicionales hipotéticos
Tasa = 62.10680555 − 100 × 155.26701388 / 255,362 = 62.04600284%
```

La pantalla redondea **62.11% → 62.05%**, reducción de **0.0608 pp**. El cambio es pequeño y el municipio permanece en nivel alto: el escenario no garantiza pasar a verde. La respuesta de 25% es un supuesto ilustrativo, sin evidencia de efectividad. Se usa SV+NV 2024, no electorado proyectado. La cifra decimal expresa una expectativa algebraica, no una cuenta de personas observadas.

## Decisión que se puede defender

Revisar este territorio dentro de una lista de capacidad limitada, comprobar calidad y viabilidad y explorar un piloto. La evidencia disponible no respalda asignación definitiva ni promesas de participantes adicionales.

Fuentes locales: `demo/data/resultados.json` (clave 23008), `demo/decision.js` (ranking, estabilidad y escenario). El archivo `caso_municipal.json` reproduce los valores sin redondear mediante `generar_caso.cjs`.
