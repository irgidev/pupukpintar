# -*- coding: utf-8 -*-
"""
Pelatihan model PupukPintar dan penyimpanan metrik.

Jalankan sekali sebelum server hidup:
    python train.py

Keluaran:
    model.joblib      : RandomForestRegressor multi-output siap disajikan
    metrik_model.json : metrik 5-fold CV, metrik holdout, feature importance

Metrik pada berkas ini adalah angka yang dikutip Laporan Akhir (Bab 4, 7, 8).
"""

import json
import time

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, train_test_split, cross_val_predict

from data_proxy import KOLOM_X, bangun_dataset, susun_X

HARA = ["Dosis_N", "Dosis_P", "Dosis_K"]
AMBANG_DEVISI = 0.125  # tengah toleransi SRS 10-15%


def latih():
    df = bangun_dataset(n=6000, seed=42)
    X = susun_X(df)
    y = df[HARA]

    metrik = {"n_data": int(len(df)), "seed": 42, "model": "RandomForestRegressor(n_estimators=300, min_samples_leaf=3)"}

    # 1) 5-fold cross-validation pada seluruh data (metrik utama, sama dengan PoC)
    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1)
    t0 = time.perf_counter()
    pred_cv = cross_val_predict(rf, X, y, cv=KFold(5, shuffle=True, random_state=42))
    metrik["cv_waktu_detik"] = round(time.perf_counter() - t0, 1)

    dev = np.abs(pred_cv - y.values) / y.values
    metrik["cv"] = {
        "agreement_persen": round(float((dev <= AMBANG_DEVISI).all(axis=1).mean() * 100), 1),
        "agreement_per_hara": {h: round(float((dev[:, i] <= AMBANG_DEVISI).mean() * 100), 1) for i, h in enumerate(HARA)},
        "r2": {h: round(r2_score(y[h], pred_cv[:, i]), 3) for i, h in enumerate(HARA)},
        "mae_kg": {h: round(mean_absolute_error(y[h], pred_cv[:, i]), 1) for i, h in enumerate(HARA)},
    }

    # 2) Holdout 20% yang tidak pernah disentuh saat pemilihan model
    #    (data uji terpisah dari data latih, syarat Bab 8 laporan)
    X_latih, X_uji, y_latih, y_uji = train_test_split(X, y, test_size=0.2, random_state=7)
    rf.fit(X_latih, y_latih)
    pred_uji = rf.predict(X_uji)
    dev_uji = np.abs(pred_uji - y_uji.values) / y_uji.values
    metrik["holdout"] = {
        "n_uji": int(len(X_uji)),
        "agreement_persen": round(float((dev_uji <= AMBANG_DEVISI).all(axis=1).mean() * 100), 1),
        "agreement_per_hara": {h: round(float((dev_uji[:, i] <= AMBANG_DEVISI).mean() * 100), 1) for i, h in enumerate(HARA)},
        "r2": {h: round(r2_score(y_uji[h], pred_uji[:, i]), 3) for i, h in enumerate(HARA)},
        "mae_kg": {h: round(mean_absolute_error(y_uji[h], pred_uji[:, i]), 1) for i, h in enumerate(HARA)},
    }

    # 3) Latih model final pada seluruh data untuk disajikan di aplikasi
    rf_full = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1)
    rf_full.fit(X, y)

    # 4) Latensi satu prediksi pada model final (rata-rata 50 panggilan)
    contoh = X.iloc[[0]]
    rf_full.predict(contoh)  # pemanasan
    t_list = []
    for _ in range(50):
        t1 = time.perf_counter()
        rf_full.predict(contoh)
        t_list.append((time.perf_counter() - t1) * 1000)
    metrik["latensi_ms"] = {"mean": round(float(np.mean(t_list)), 1), "p95": round(float(np.percentile(t_list, 95)), 1)}

    metrik["feature_importance"] = {
        kolom: round(float(imp), 4) for kolom, imp in sorted(zip(KOLOM_X, rf_full.feature_importances_), key=lambda t: -t[1])
    }

    joblib.dump(rf_full, "model.joblib")
    with open("metrik_model.json", "w", encoding="utf-8") as f:
        json.dump(metrik, f, ensure_ascii=False, indent=2)
    print(json.dumps(metrik["cv"], ensure_ascii=False))
    print(json.dumps(metrik["holdout"], ensure_ascii=False))
    print("latensi_ms:", metrik["latensi_ms"])


if __name__ == "__main__":
    latih()
