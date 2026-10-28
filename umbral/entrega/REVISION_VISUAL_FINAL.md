# Revisión visual y funcional final

Fecha: 28 de octubre de 2026. Navegador: Microsoft Edge local. Pruebas de escritorio y emulación móvil; no se utilizó un teléfono físico.

## Alcance comprobado

- Años 2009, 2012, 2015, 2018, 2021, 2024 y proyección 2027. Al consultar históricos, el selector de modelo y los escenarios futuros quedan desactivados u ocultos según corresponde.
- Cinco métodos: HistGradientBoosting, LightGBM, CatBoost, Ridge y referencia. También filtros de catálogo, criterios de prioridad, estabilidad y distribución.
- Consulta de planes de las 32 entidades; selección de municipio, estado y país; alcance predeterminado por población y edición manual.
- Siete opciones de acción, incluidas ausencia de acción y confianza institucional con efecto cero; coberturas cero, positivas e inválidas; mapas base, con intervención y diferencias.
- Buscador, selección de municipios, clic derecho para retroceder, recorrido guiado, navegación por secciones y paneles desplegables (37 visibles en el caso revisado).
- Descargas de consulta y distribución CSV/Excel, estructura del Excel y correspondencia con el escenario activo. Se conservaron los enlaces a PDF y archivos locales. No se abrió el diálogo de impresión del sistema ni se realizaron envíos externos.
- Capturas de las secciones de la página a 1440, 768, 390 y 360 píxeles. Controles avanzados, simulación, metodología y mapas pareados inspeccionados también en formato móvil.

## Problemas corregidos

1. La reconstrucción del mapa podía restaurar la leyenda extensa anterior. Ahora actualiza de nuevo la información compacta y la guía de navegación.
2. Al desplazarse a elementos internos, las secciones con recorte podían conservar un desplazamiento interno y ocultar sus títulos. Se usa recorte sin contenedor desplazable y se calcula el margen de navegación según la altura real de las cabeceras.
3. La línea decorativa lateral conservaba altura de escritorio en móvil. Se redujo a una línea horizontal.
4. Una nota técnica seguía visible bajo el mapa durante las simulaciones. Se integró al desplegable de lectura.
5. Los mapas comparados podían conservar un zoom excesivo al reducir el ancho. Al cambiar el tamaño se invalida la composición y se reencuadra el territorio. La prueba adicional comprueba que ambos mapas contienen sus límites completos.

## Evidencia

`demo/verificacion/demo7/resultado_recorrido_completo.json` conserva la matriz ampliada; `resultado.json` corresponde a la aceptación de la versión final. Las capturas `auditoria_*` documentan las vistas. `verificacion_paquete.json` registra la comprobación del ZIP y su huella actual.

Las pruebas no presentaron excepciones de JavaScript ni desbordamiento horizontal de la página en los cuatro tamaños. Las tablas extensas mantienen su desplazamiento dentro del contenedor. Se revisaron visualmente las capturas, además de las comprobaciones geométricas.
