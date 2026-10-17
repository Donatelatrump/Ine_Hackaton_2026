# Umbral demo7

Abrir `demo7.html` con toda la carpeta de recursos. Funciona mediante `file://` y con el servidor local existente; el documento de planes sigue incrustado en el JavaScript generado.

## Construcción

Desde la raíz del proyecto:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_demo7.py
```

La configuración `build.demo7.config.json` reutiliza datos, dominio y cartografía de demo6. Las vistas y la experiencia de demo7 están en `src/demo7/`; los ajustes visuales están en `styles/demo7.css`. Los recursos generados son `assets/demo7.js`, `assets/demo7.css` y `assets/build.demo7.json`. La construcción no modifica demo6.

## Recorrido

En 03 el orden de lectura es diagnóstico, plan estatal recomendado, impacto aproximado, supuestos y simulación por actividad, distribución municipal y mapas. El impacto aparece inmediatamente después del plan y antes de los controles de simulación. Todo permanece en la misma tarjeta, seguido del simulador general.

La vista inicial prioriza actividades, cifras y controles. Los argumentos de cada recomendación, responsables, fuentes, evidencia y límites se consultan en desplegables. Los controles de la actividad y del simulador permanecen visibles. Las cifras del comparador se actualizan aunque el mapa esté fuera de pantalla; las geometrías se redibujan cuando la vista entra en pantalla.

1. El botón «Ver un caso de ejemplo» prepara la clave histórica 23008, proyección de 2027 y el ejemplo de SMS para 1,000 personas. No cambia el modelo elegido.
2. La barra de contexto conserva territorio, año y tipo de dato durante el recorrido. En históricos ofrece volver a 2027.
3. La tarjeta estatal muestra diagnóstico agregado, comparación 2027, votos adicionales, mejora en puntos porcentuales y personas alcanzadas. Cada actividad explica qué dato orienta explorarla y sus límites. El cálculo automático usa una actividad concreta con alcance y rango de efecto editables; los parámetros se conservan por estado y actividad durante la sesión. Los alcances iniciales son supuestos del 10 % del grupo aproximado; cuando falta el dato del grupo comienzan en cero. Las actividades no informativas sin estimador local comienzan con efecto cero. Ningún coeficiente representa un efecto causal comprobado del plan completo.
4. La comparación estatal usa las asignaciones reales de la simulación dentro del estado; incluye municipios no atendidos en el promedio. La comparación de mapas usa el territorio elegido en el simulador. Ambas conservan método y filtros.
5. La vista inicial «Ver cambio exacto (pp)» muestra diferencias con escala relativa al cambio máximo del escenario: blanco sin cambio, azul para reducciones y gris sin estimación. Las tarjetas muestran reducción media, votos adicionales y municipios que mejoran; también se indica cuántos cruzan los umbrales del semáforo. Los detalles al pasar por cada municipio incluyen tasas con cinco decimales. «Comparar niveles de riesgo» conserva los dos mapas con los mismos umbrales de riesgo. Las tres vistas sincronizan zoom y encuadre. La escala de diferencias y los umbrales de riesgo tienen significados distintos y leyendas propias; la magnitud calculada no se modifica para hacer más visible el color.
6. Las órbitas pueden pausarse; también se detienen al enfocar perfiles, al pasar el cursor y cuando la portada queda fuera de pantalla. Se respeta la preferencia de movimiento reducido.
7. «¿Cómo se distribuyen los recursos?» muestra cobertura municipal, prioridad, atención, pendientes y falta de estimación. Permite filtrar, paginar y descargar toda la distribución CSV. El recurso es alcance en personas; no se inventan costos monetarios. En distribución proporcional, ordenar por prioridad no significa concentrar la asignación en los primeros lugares.
8. «Descargar ficha» genera un HTML autónomo imprimible con territorio, método, diagnóstico, acción, alcance, efecto, asignación, fuentes y límites. «Imprimir / guardar PDF» abre la misma ficha para impresión; el navegador permite guardarla como PDF. La ficha resume los primeros cinco municipios atendidos; la distribución completa se entrega en CSV.
9. «Recorrido para presentar» prepara un caso con HistGradientBoosting, Quintana Roo e información práctica para el 10 % de la base estatal. Guía cinco pasos: diagnóstico, predicción, acción, recursos/resultado y ficha. Se puede cerrar en cualquier momento con el botón o Escape; no avanza automáticamente.

## Cálculo por actividad

Se distribuye la cobertura declarada por prioridad o proporcionalmente a SV+NV 2024. Por municipio, votos adicionales = mínimo entre personas alcanzadas × efecto/100 y abstencionistas esperados dentro de las personas alcanzadas. Se repite el cálculo con el efecto inferior y superior. La tasa posterior se calcula sobre la base territorial completa estimable, incluidos los municipios no atendidos. Se simula una sola actividad: no se suman efectos de campañas ni se presume que sus personas destinatarias sean distintas.

Los parámetros requieren cobertura entera no negativa, limitada a la base observable, y efectos que cumplan 0 ≤ inferior ≤ central ≤ superior ≤ 100 pp. Un escenario inválido deja de mostrar resultados y desactiva la ficha hasta corregirlo. La composición agregada de grupos orienta una propuesta, sin identificar destinatarios individuales.

## Interpretación

Las actividades del plan documental no tienen un efecto conjunto validado. El simulador estima una acción elegida y una cobertura explícita. El rango de efecto depende de la acción y no constituye un intervalo de confianza para 2027. La base SV+NV 2024 tampoco representa el electorado proyectado de 2027.

La página ofrece enlaces al reporte, presentación, datos y requisitos oficiales. Las cartas, registro, permisos y vigencia de documentos se verifican por separado: la interfaz no certifica cumplimiento administrativo.

## Revisión

`tmp/revisar_demo7.py` recorre la versión local con Edge sin ventana y guarda capturas y resultados en `tmp/demo7/`. Comprueba arranque, avatares, ejemplo municipal, preparación estatal, tres mapas, ancho móvil, cambio histórico y pausa. Verifica también edición y conservación por actividad, efecto cero sin estimador, validación de rangos, suma de asignaciones, pendientes, filtros, descargas HTML/CSV, impresión PDF de una página para el caso revisado y los cinco pasos del recorrido. No requiere paquetes Python adicionales.
