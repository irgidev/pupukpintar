# -*- coding: utf-8 -*-
"""
Pembangkit data contoh zona peta hara.

Membuat 12 zona representatif wilayah Bogor dengan nilai pH, N, P, K, dan
tekstur yang menyebar pada rentang data latih. Nilai ini adalah CONTOH
representasi sederhana dari peta hara 191 area SAFRONS, bukan hasil uji
laboratorium. Label keterangan itu ikut tersimpan di berkas JSON.

Jalankan dari folder app/backend:
    python ../frontend/data/gen_zona.py
"""

import json
import os

import numpy as np

ZONA = [
    ("Cibinong", -6.481, 106.888), ("Ciampea", -6.556, 106.694),
    ("Dramaga", -6.566, 106.727), ("Leuwiliang", -6.587, 106.652),
    ("Megamendung", -6.641, 106.933), ("Cisarua", -6.700, 106.945),
    ("Gunung Sindur", -6.352, 106.683), ("Parung", -6.428, 106.730),
    ("Rumpin", -6.377, 106.610), ("Nanggung", -6.590, 106.560),
    ("Sukaraja", -6.565, 106.833), ("Cigeulis", -6.490, 106.810),
]

rng = np.random.default_rng(2026)
tekstur = ["Lempung", "Lempung Liat", "Liat"]

zona_list = []
for i, (nama, lat, lon) in enumerate(ZONA):
    zona_list.append({
        "id": f"Z{i+1:02d}",
        "nama": nama,
        "lat": lat,
        "lon": lon,
        # kolom grid untuk gambar peta SVG (x, y dalam viewBox 360x300)
        "grid_x": 30 + (i % 4) * 84 + int(rng.integers(-10, 11)),
        "grid_y": 36 + (i // 4) * 82 + int(rng.integers(-8, 9)),
        "pH": round(float(rng.uniform(4.4, 7.0)), 1),
        "n_persen": round(float(rng.uniform(0.12, 0.75)), 2),
        "p_ppm": round(float(rng.uniform(4.0, 65.0)), 1),
        "k_me100g": round(float(rng.uniform(0.08, 0.85)), 2),
        "tekstur": tekstur[int(rng.integers(0, 3))],
    })

data = {
    "keterangan": (
        "Data contoh representasi sederhana peta hara wilayah Bogor "
        "(terinspirasi peta 191 area SAFRONS). Nilai per zona dibangkitkan "
        "pada rentang data latih untuk kebutuhan demo, bukan hasil uji laboratorium."
    ),
    "zona": zona_list,
}

keluar = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zona_peta.json")
with open(keluar, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("zona_peta.json tersimpan:", keluar)
