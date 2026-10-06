"""Empaqueta todo el workspace con inventario SHA256 y validación CRC."""
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'Ine_Hackaton_completo.zip'
TEMP = ROOT / 'Ine_Hackaton_completo.zip.part'
MANIFEST = ROOT / 'MANIFIESTO_PAQUETE.json'

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [name for name in dirs if name != '.git']
        files.extend(p for name in names if (p := Path(base) / name) not in {DEST, TEMP, MANIFEST})
    files.sort()
    inventory = [{'ruta': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in files]
    MANIFEST.write_text(json.dumps({'created_utc': datetime.now(timezone.utc).isoformat(), 'root': ROOT.name, 'files': inventory, 'note': 'Incluye archivos del proyecto salvo metadatos .git, ZIP de salida y temporal; manifiesto incluido sin autorreferencia.'}, ensure_ascii=False, indent=2), encoding='utf-8')
    files.append(MANIFEST)
    print(f'Empaquetando {len(files)} archivos', flush=True)
    with zipfile.ZipFile(TEMP, 'w', allowZip64=True) as z:
        for p in files:
            compression = zipfile.ZIP_STORED if p.suffix.lower() in {'.zip', '.png', '.jpg', '.jpeg', '.pdf'} else zipfile.ZIP_DEFLATED
            z.write(p, arcname=ROOT.name + '/' + p.relative_to(ROOT).as_posix(), compress_type=compression, compresslevel=3)
    with zipfile.ZipFile(TEMP) as z:
        assert len(z.infolist()) == len(files)
        bad = z.testzip()
        assert bad is None, f'CRC inválido: {bad}'
        assert json.loads(z.read(ROOT.name + '/' + MANIFEST.name))['files'] == inventory
    os.replace(TEMP, DEST)
    print(json.dumps({'zip': str(DEST), 'files': len(files), 'bytes': DEST.stat().st_size, 'sha256': sha256(DEST), 'crc': 'OK'}, ensure_ascii=True), flush=True)

if __name__ == '__main__':
    main()
