# -*- coding: utf-8 -*-
"""
Evaluasi tambahan untuk Laporan Akhir:
1) model baseline (prediksi rata-rata per komoditas dan regresi linear)
   dibandingkan Random Forest pada holdout yang sama,
2) kalibrasi keyakinan: kesepakatan per kelompok keyakinan,
3) ringkasan contoh prediksi untuk tabel laporan.

Jalankan dari root repositori:
    python tests/evaluasi_tambahan.py
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app", "backend"))
os.chdir(os.path.join(ROOT, "app", "backend"))

from data_proxy import bangun_dataset, susun_X  # noqa: E402
from sklearn.linear_model import LinearRegression  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.ensemble import RandomForestRegressor  # noqa: E402

HARA = ["Dosis_N", "Dosis_P", "Dosis_K"]
AMBANG = 0.125

df = bangun_dataset(n=6000, seed=42)
X = susun_X(df)
y = df[HARA]
X_l, X_u, y_l, y_u = train_test_split(X, y, test_size=0.2, random_state=7)

hasil = {}

# ---------- 1) baseline ----------
rata = y_l.groupby(X_l["Komoditas_Padi"]).mean()  # rata-rata per komoditas
is_padi_uji = X_u["Komoditas_Padi"].to_numpy().astype(bool)
pred_mean = np.where(is_padi_uji[:, None],
                     rata.loc[True][HARA].to_numpy()[None, :],
                     rata.loc[False][HARA].to_numpy()[None, :])
dev_mean = np.abs(pred_mean - y_u.values) / y_u.values
hasil["baseline_mean"] = {
    "agreement_persen": round(float((dev_mean <= AMBANG).all(axis=1).mean() * 100), 1),
    "mae_kg": {h: round(float(np.abs(pred_mean[:, i] - y_u[h].values).mean()), 1) for i, h in enumerate(HARA)},
}

lin = LinearRegression().fit(X_l, y_l)
pred_lin = lin.predict(X_u)
dev_lin = np.abs(pred_lin - y_u.values) / y_u.values
hasil["baseline_linear"] = {
    "agreement_persen": round(float((dev_lin <= AMBANG).all(axis=1).mean() * 100), 1),
    "mae_kg": {h: round(float(np.abs(pred_lin[:, i] - y_u[h].values).mean()), 1) for i, h in enumerate(HARA)},
}

rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1).fit(X_l, y_l)
pred_rf = rf.predict(X_u)
dev_rf = np.abs(pred_rf - y_u.values) / y_u.values
hasil["model_utama_rf"] = {
    "agreement_persen": round(float((dev_rf <= AMBANG).all(axis=1).mean() * 100), 1),
    "mae_kg": {h: round(float(np.abs(pred_rf[:, i] - y_u[h].values).mean()), 1) for i, h in enumerate(HARA)},
}

# ---------- 2) kalibrasi keyakinan ----------
pohon = np.stack([est.predict(X_u.to_numpy()) for est in rf.estimators_])  # (n_pohon, n, 3)
rata_pohon = pohon.mean(axis=0)      # (n, 3)
std_pohon = pohon.std(axis=0)
cv_relatif = (std_pohon / np.maximum(rata_pohon, 1e-9)).mean(axis=1)  # (n,)
keyakinan = np.clip(1 - cv_relatif * 2, 0, 1)

kelompok = [(">= 0,85 (yakin)", keyakinan >= 0.85),
            ("0,70 sampai 0,85 (cukup yakin)", (keyakinan >= 0.70) & (keyakinan < 0.85)),
            ("< 0,70 (tidak yakin)", keyakinan < 0.70)]
hasil["kalibrasi"] = []
for nama, mask in kelompok:
    if mask.sum() == 0:
        continue
    dev_k = dev_rf[mask]
    hasil["kalibrasi"].append({
        "kelompok": nama,
        "jumlah": int(mask.sum()),
        "proporsi_persen": round(float(mask.mean() * 100), 1),
        "agreement_persen": round(float((dev_k <= AMBANG).all(axis=1).mean() * 100), 1),
        "rata_keyakinan": round(float(keyakinan[mask].mean()), 2),
    })

# ---------- 3) contoh prediksi untuk laporan ----------
contoh_input = [
    {"pH": 5.4, "n_persen": 0.35, "p_ppm": 7.0, "k_me100g": 0.18, "tekstur": "Lempung",
     "Komoditas": "Padi", "Target_Hasil": 6.0, "Musim": "Hujan"},
    {"pH": 6.8, "n_persen": 0.70, "p_ppm": 45.0, "k_me100g": 0.60, "tekstur": "Lempung Liat",
     "Komoditas": "Jagung", "Target_Hasil": 9.0, "Musim": "Kemarau"},
]
from data_proxy import KOLOM_X  # noqa: E402
import pandas as pd  # noqa: E402

contoh_out = []
for c in contoh_input:
    baris = {
        "pH": c["pH"], "N_persen": c["n_persen"], "P_ppm": c["p_ppm"], "K_me100g": c["k_me100g"],
        "Target_Hasil": c["Target_Hasil"],
        "Tekstur_Lempung": 0, "Tekstur_Lempung Liat": 0, "Tekstur_Liat": 0,
        "Komoditas_Padi": 0, "Komoditas_Jagung": 0, "Musim_Hujan": 0, "Musim_Kemarau": 0,
    }
    baris[f"Tekstur_{c['tekstur']}"] = 1
    baris[f"Komoditas_{c['Komoditas']}"] = 1
    baris[f"Musim_{c['Musim']}"] = 1
    Xc = pd.DataFrame([baris])[KOLOM_X]
    pred = rf.predict(Xc)[0]
    pk = np.stack([est.predict(Xc.to_numpy())[0] for est in rf.estimators_])
    k = float((pk.std(axis=0) / np.maximum(pk.mean(axis=0), 1e-9)).mean())
    contoh_out.append({
        "input": c,
        "dosis_model_kg_ha": [round(float(v)) for v in pred],
        "dosis_pakar_kg_ha": [round(float(v), 1) for v in y.loc[(df.pH == c['pH']) & (df.N_persen == c['n_persen'])].iloc[0][HARA].values] if False else None,
        "keyakinan": round(max(0.0, min(1.0, 1 - k * 2)), 2),
    })

hasil["contoh"] = contoh_out

keluar = os.path.join(ROOT, "tests", "hasil_evaluasi_tambahan.json")
with open(keluar, "w", encoding="utf-8") as f:
    json.dump(hasil, f, ensure_ascii=False, indent=2)
print(json.dumps(hasil, ensure_ascii=False, indent=2))
