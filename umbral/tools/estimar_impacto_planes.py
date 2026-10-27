"""Agrega a cada plan un escenario indicativo de impacto con la base de Umbral."""
from collections import defaultdict
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "umbral/demo/data/resultados.json"
DOC = ROOT / "docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md"

# Supuesto de referencia ya usado por la simulación de información institucional.
COVERAGE = 0.10
EFFECT_LOW_PP = 0.3
EFFECT_CENTRAL_PP = 1.5
EFFECT_HIGH_PP = 3.0


def normalize(value):
    decomposed = unicodedata.normalize("NFD", str(value or ""))
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold().strip()


def rounded(value):
    step = 10 if value < 1_000 else 100 if value < 10_000 else 1_000
    return int(step * round(value / step))


def main():
    results = json.loads(DATA.read_text(encoding="utf-8"))["municipios"]
    bases = defaultdict(float)
    names = {}
    for row in results:
        risk, observed = row.get("risk"), row.get("observed")
        if isinstance(risk, (int, float)) and 0 <= risk <= 100 and isinstance(observed, (int, float)) and observed > 0:
            key = str(row["state"]).zfill(2)
            bases[key] += observed
            names[key] = row["state_name"]

    heading_to_key = {normalize(name): key for key, name in names.items()}
    heading_to_key.update({
        "coahuila": "05",
        "estado de mexico": "15",
        "michoacan": "16",
        "veracruz": "30",
    })

    text = DOC.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if not line.startswith("- **Impacto orientativo:**")]
    if any(line == "## 8. Estimación aproximada de impacto" for line in lines):
        start = lines.index("## 8. Estimación aproximada de impacto")
        lines = lines[:start]

    output = []
    current_key = None
    inserted = set()
    heading_pattern = re.compile(r"^###\s+\d+(?:\.\d+)?\s+(.+?)\s*$")
    for line in lines:
        output.append(line)
        heading = heading_pattern.match(line)
        if heading:
            current_key = heading_to_key.get(normalize(heading.group(1)))
        if current_key and current_key not in inserted and line.startswith("- **Horizonte:**"):
            base = bases.get(current_key, 0)
            low = rounded(base * COVERAGE * EFFECT_LOW_PP / 100)
            central = rounded(base * COVERAGE * EFFECT_CENTRAL_PP / 100)
            high = rounded(base * COVERAGE * EFFECT_HIGH_PP / 100)
            output.append(
                "- **Impacto orientativo:** +0.03 a +0.30 puntos porcentuales de participación "
                "(escenario central: +0.15 pp), equivalentes a aproximadamente "
                f"**{low:,}–{high:,} votos adicionales** (central: **{central:,}**) en municipios estimables."
            )
            inserted.add(current_key)

    missing = set(bases) - inserted
    if missing:
        raise ValueError("No se encontró el apartado de horizonte para las entidades: " + ", ".join(sorted(missing)))

    output.extend([
        "",
        "## 8. Estimación aproximada de impacto",
        "",
        "Las cifras por estado son un escenario de referencia, no una predicción ni un efecto comprobado del conjunto de acciones. "
        "Su cálculo supone alcanzar al 10 % de la base observable SV+NV de 2024 en municipios con estimación válida para 2027, "
        "y aplicar a las personas alcanzadas el supuesto de información institucional práctica de la demo: 0.3–3.0 pp de efecto "
        "(valor central: 1.5 pp). Por eso el cambio estatal equivale a +0.03–+0.30 pp (central: +0.15 pp).",
        "",
        "Los votos adicionales se calculan como base elegible × 10 % de cobertura × efecto supuesto, y se redondean para evitar "
        "falsa precisión. La base excluye municipios sin estimación válida y no representa la lista nominal ni el electorado de 2027. "
        "El supuesto de efecto procede de evidencia heterogénea y no está validado para estas acciones, estados o elección; no se suman "
        "los efectos de varias actividades. Se requiere definir presupuesto, alcance real y una evaluación local antes de atribuir impacto.",
        "",
    ])
    DOC.write_text("\n".join(output), encoding="utf-8")
    print(f"Impacto orientativo agregado en {len(inserted)} planes; base estimable 2024 y supuesto 10 % de cobertura.")


if __name__ == "__main__":
    main()
