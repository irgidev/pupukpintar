# -*- coding: utf-8 -*-
"""
Pembangkit ulang grafik PoC (grafik_poc.png) langsung dari metrik final
app/backend/metrik_model.json agar angka pada grafik, tabel laporan, dan
aplikasi selalu sama.

Jalankan dari root repositori:
    python poc/buat_grafik_poc.py
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "app", "backend", "metrik_model.json"), encoding="utf-8") as f:
    metrik = json.load(f)

cv = metrik["cv"]
agreement = cv["agreement_persen"]
hara = ["N", "P (P2O5)", "K (K2O)"]
nilai_mae = [cv["mae_kg"]["Dosis_N"], cv["mae_kg"]["Dosis_P"], cv["mae_kg"]["Dosis_K"]]
nilai_r2 = [cv["r2"]["Dosis_N"], cv["r2"]["Dosis_P"], cv["r2"]["Dosis_K"]]

fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4))

ax = axes[0]
ax.bar(["Target minimum\nSRS", "Target SRS", "Hasil PoC\n(seluruh hara)"],
       [85, 90, agreement], color=["#9fb3c8", "#9fb3c8", "#2e6f4e"], width=0.55)
ax.set_ylim(0, 100)
ax.set_ylabel("Rekomendasi dalam rentang pakar (%)")
for i, v in enumerate([85, 90, agreement]):
    ax.text(i, v + 1.5, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=9)
ax.set_title("Agreement vs target SRS (5-fold CV)", fontsize=10)

ax = axes[1]
bars = ax.bar(hara, nilai_mae, color="#b07d3c", width=0.5)
ax.set_ylabel("MAE 5-fold CV (kg/ha)")
ax.set_ylim(0, max(nilai_mae) * 1.4)
for b, m, r in zip(bars, nilai_mae, nilai_r2):
    ax.text(b.get_x() + b.get_width() / 2, m + 0.08, f"{m} kg/ha\nR2={r}", ha="center", fontsize=8.5)
ax.set_title("Galat prediksi per unsur hara", fontsize=10)

fig.suptitle(f"PoC PupukPintar: Random Forest Regressor (n={metrik['n_data']:,}, 5-fold CV)".replace(",", "."), fontsize=10.5)
fig.tight_layout()
keluar = os.path.join(ROOT, "poc", "grafik_poc.png")
fig.savefig(keluar, dpi=200)
print("tersimpan:", keluar)
