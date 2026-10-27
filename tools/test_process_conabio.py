"""Regresión del vínculo municipal entre CONABIO y la base de la demo."""

import json
import unittest

import geopandas as gpd

import process_conabio


class RemapeoConabioTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gdf = gpd.read_file(process_conabio.SHP)
        cls.gdf["clave_municipio_ine"] = (
            cls.gdf["cve_ent"].astype(str).str.zfill(2)
            + cls.gdf["cve_mun"].astype(str).str.zfill(3)
        )
        cls.claves_base = {
            municipio["key"]
            for municipio in json.loads(
                process_conabio.RESULTADOS.read_text(encoding="utf-8")
            )["municipios"]
        }

    def test_remap_cubre_la_base_y_resuelve_homonimos_por_orden(self):
        error = None
        try:
            pares = process_conabio.remapear_por_nombre(self.gdf)
        except SystemExit as exc:
            error = str(exc)
            pares = {}

        self.assertIsNone(error, f"El remapeo debe cubrir la capa completa: {error}")
        self.assertEqual(len(pares), len(self.gdf))
        self.assertEqual(set(pares.values()), self.claves_base)

        self.assertEqual(pares["20208"], "20208")
        self.assertEqual(pares["20209"], "20209")
        self.assertEqual(pares["20318"], "20316")
        self.assertEqual(pares["20319"], "20317")
        self.assertEqual(pares["24059"], "24028")


if __name__ == "__main__":
    unittest.main()
