# Trabajo en equipo: track 2

El desarrollo activo se limita a `umbral/`.
Las ramas contienen el proyecto completo; esta distribución establece responsabilidades, no restricciones de Git.

| Rama | Responsabilidad | Archivos principales |
| --- | --- | --- |
| `main` | Versión integrada y revisada | Todo el proyecto |
| `algoritmo` | Modelos, evaluación y pruebas | `modelado/` |
| `web` | Interfaz, mapa y escenarios | `demo/`, excepto datos generados |
| `datos` | Fuentes, auditoría y preparación | `auditoria/`, `cartografia/`, `datos_preparados/`, descargador y catálogos |
| `entrega` | Reporte, presentación y documentación | `entrega/` y documentos generales |

Para dos personas, una puede trabajar en `algoritmo` y otra en `web`. Cada persona debe usar su propio clon; cambiar de rama en la misma carpeta afecta a todos los procesos que la usan.

## Empezar y actualizar

Desde un clon propio y con el árbol de trabajo limpio:

```powershell
git fetch origin
git switch --track origin/algoritmo
git merge origin/main
```

Sustituir `algoritmo` por el área asignada. Si la rama ya existe localmente, usar `git switch algoritmo`. Antes de empezar otra tarea y antes de abrir un pull request, ejecutar `git fetch origin` y `git merge origin/main`. Resolver conflictos y repetir las pruebas.

Si ambos trabajan en la misma área, crear ramas por tarea desde `origin/main`, por ejemplo `algoritmo/mejorar-ridge` o `web/filtros`. Coordinarse antes de compartir una rama.

## Archivos compartidos

`modelado/salidas/resultados.json` alimenta `demo/data/resultados.json` y los datos embebidos. Acordar cambios en claves, campos, unidades y valores ausentes antes de modificar ese contrato.

La persona que cambia el algoritmo coordina la regeneración de `modelado/salidas/` y `demo/data/`, incluido `datos_embebidos.js`. La rama `web` consume esos archivos y evita editarlos manualmente. `demo/preparar_datos.py` es compartido: acordar quién lo modifica en cada tarea. La preparación completa puede requerir cartografía original que ya no está en el estado actual del repositorio.

La rama `datos` coordina cambios de insumos con `algoritmo`; `entrega` regenera documentos después de integrar modelo y demo. Evitar regenerar PDF, PPTX e imágenes de evidencia en dos ramas al mismo tiempo.

## Comprobar e integrar

Desde la raíz, según el área modificada:

```powershell
python -m unittest discover -s umbral/modelado/tests
node --test umbral/demo/decision.test.cjs
python umbral/modelado/verificar_artefactos.py
```

Python requiere las dependencias de `modelado/requirements.txt`. Comprobar artefactos cuando cambien datos o resultados. Para cambios visuales, comprobar escritorio y móvil; para documentos, usar `entrega/verificar_entrega.py` con sus dependencias instaladas.

```powershell
git add <archivos-de-la-tarea>
git commit -m "Describir el cambio"
git push -u origin algoritmo
```

Abrir un pull request hacia `main`, describir el cambio y las comprobaciones, y pedir revisión a la otra persona. Integrar de uno en uno; después actualizar las demás ramas desde `origin/main`. Evitar push directo a `main` y force push en ramas compartidas.

Estas reglas son acuerdos de trabajo. Para hacerlas obligatorias, un administrador debe configurar un ruleset de GitHub para `main` que exija pull requests y una aprobación, y bloquee force push y eliminación. Crear ramas por sí solo no habilita esa protección.

## Organización de demo6

La interfaz vigente es demo7. Sus cambios propios están en `demo/src/demo7/` y `demo/styles/demo7.css`; comparte el motor descrito abajo. Reconstruir con `python umbral/tools/construir_demo7.py` y comprobar con `python umbral/demo/verificar_demo7.py`. Ver [guía vigente](../umbral/demo/DEMO7.md). Un cambio en fuentes compartidas requiere reconstruir y comprobar ambas versiones.

El código actual está en `demo/src/demo6/` y los estilos propios en `demo/styles/demo6/`, dentro del track. Las vistas reciben dependencias explícitas; las fórmulas descriptivas pertenecen a `domain/analytics.js`. Consultar `arquitectura/README.md` antes de cambiar rutas. Las entradas HTML y los comandos de generadores se conservan. Los datos publicados se modifican mediante su generador.

Después de modificar fuentes JS/CSS, ejecutar `python umbral/tools/construir_web.py` y compartir también los recursos actualizados de `demo/assets/`. El orden está en `demo/build.config.json`. El estado interno es privado: las pruebas de navegador usan `Umbral6.inspect()`. El arranque completo emite `umbral:ready`; no añadir sondeos con intervalos ni sobrescribir funciones del motor para integrar componentes.
