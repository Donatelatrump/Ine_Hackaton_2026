# Caso municipal: de una prioridad a una propuesta revisable

6 de octubre de 2026. Caso 23008, **SOLIDARIDAD**, Quintana Roo: nombre del catálogo histórico utilizado, no certificación de denominación o límites actuales.

## Configuración reproducible

Abrir `demo/index.html`. En el paso 3 elegir municipio, Quintana Roo, clave 23008, SMS Suecia y cobertura total de 1,000 personas. Mantener Ridge y catálogo constante. La distribución por prioridad o proporcional coincide al simular un solo municipio.

Los puestos 1/3 y la estabilidad 4/6 de la tabla siguiente se calculan **como referencia nacional top50** sobre 1,144 municipios estimables con catálogo constante. No son el puesto o la estabilidad recalculados al filtrar un único municipio. `generar_caso.cjs` reproduce ambos universos por separado.

## Evidencia del caso

| Variable | Valor | Significado |
|---|---:|---|
| Puesto Ridge | 1 de 1,144 estimables | Referencia nacional con catálogo constante |
| Puesto de referencia | 3 | Misma cohorte y criterio |
| Abstención 2021 | 66.30% | Última intermedia observada |
| Abstención 2024 | 48.96% | Presidencial observada; otro tipo electoral |
| Estimación exploratoria 2027 | 62.11% | Ridge, no tasa validada |
| NS 2021 / 2024 | 9.60% / 2.28% | Calidad de antecedentes |
| SV+NV 2024 | 255,362 | Base observable histórica |
| LN 2024 | 261,323 | Incluye NS; no denominador del escenario |
| Composición 18–29 / urbana | 28.26% / 91.02% | Proporciones agregadas de LN |
| Estabilidad | 4/6, media | Seleccionado en las cuatro variantes elegibles |

Referencia y Ridge coinciden dentro de la referencia top50. Las variantes NS ≤5% no son elegibles por NS 2021. Por eso pertenece a la zona de revisión, aunque ocupe el primer lugar Ridge. Cuatro variantes de seis no equivalen a una probabilidad de acierto del 67%. Catálogo constante tampoco acredita fronteras constantes.

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

Con 1,000 personas distintas previstas para recibir un recordatorio SMS y efecto ITT externo de +0.30 puntos porcentuales:

```text
H = 1,000 × 0.30 / 100 = 3 votos adicionales esperados
Tasa posterior = 62.10680555 − 100 × 3 / 255,362 = 62.10563075%
Reducción municipal = 0.00117480 puntos porcentuales
```

El intervalo publicado de 0.13–0.48 pp corresponde a 1.3–4.8 votos esperados al trasladarlo aritméticamente a esta cobertura. No incluye incertidumbre del predictor ni de transferencia a México; no es un intervalo de efecto local. El municipio permanece en riesgo alto. Los decimales expresan expectativas, no personas observadas.

Fuente del coeficiente: Lindgren, Nyman y Oskarsson (2025), *Examining Voting Spillover Effects of Text Message Reminders*, sección Results, figura 1. [Artículo original](https://doi.org/10.1017/S0007123424000504). El experimento es de Suecia, elección europea 2019, con voto registrado y asignación a SMS; no equivale a lectores efectivos, WhatsApp o talleres.

La propuesta de talleres descrita arriba es una alternativa operativa por evaluar. **No se le asigna el coeficiente de SMS.** Para explorar talleres sin evidencia comparable se debe usar el modo personalizado con respuesta explícitamente supuesta.

## Decisión que se puede defender

Revisar este territorio dentro de una lista de capacidad limitada, comprobar calidad y viabilidad y explorar un piloto. La evidencia disponible no respalda asignación definitiva ni promesas de participantes adicionales.

Fuentes locales: `demo/data/resultados.json` (clave 23008), `demo/decision.js` (ranking, estabilidad y escenario). El archivo `caso_municipal.json` reproduce los valores sin redondear mediante `generar_caso.cjs`.
