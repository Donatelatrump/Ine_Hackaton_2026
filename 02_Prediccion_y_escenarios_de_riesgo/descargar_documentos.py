"""Descarga los cuatro PDF oficiales identificados; no descarga bases CCPC.

Uso: python descargar_documentos.py
No necesita paquetes externos. Conserva archivos existentes y registra resultados.
"""
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "fuentes.json").read_text(encoding="utf-8"))
    destination = root / "documentos_oficiales"
    destination.mkdir(exist_ok=True)
    results = []
    for document in manifest["documentos"]:
        target = destination / document["nombre"]
        result = {**document, "fecha_utc": datetime.now(timezone.utc).isoformat()}
        try:
            if target.exists():
                payload = target.read_bytes()
                state = "existente_verificado"
            else:
                request = urllib.request.Request(document["url"], headers={"User-Agent": "INE-Hackathon-Research/1.0"})
                with urllib.request.urlopen(request, timeout=20) as response:
                    payload = response.read()
                    result["url_final"] = response.url
                state = "descargado"
            if not payload.startswith(b"%PDF-"):
                raise ValueError("El archivo no tiene cabecera PDF; no se guardó la respuesta")
            if not target.exists():
                target.write_bytes(payload)
            result.update(estado=state, bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
            print(f"{state}: {document['nombre']}")
        except Exception as error:
            result.update(estado="fallido", error=str(error))
            print(f"FALLO: {document['nombre']}: {error}", file=sys.stderr)
        results.append(result)
    (root / "estado_descargas.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failures = sum(item["estado"] == "fallido" for item in results)
    print(f"PDF disponibles/verificados: {len(results) - failures}/{len(results)}. Bases CCPC: pendientes.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
