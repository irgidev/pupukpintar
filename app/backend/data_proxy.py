# -*- coding: utf-8 -*-
"""
Pembangun data latih proxy PupukPintar.

Menyalin logika PoC LKP-P6 (run_poc.py): tabel rekomendasi resmi Permentan
No. 40/2007 dan kelas interpretasi Balittanah diekstraksi menjadi baris data
tabular (strategi pelabelan semi-automated dari LKP-P4). Label dosis "pakar"
pada setiap baris dibaca dari logika tabel tersebut, lalu dikunci pada rentang
aman resmi.

Data ini adalah proxy, bukan hasil uji tanah laboratorium. Catatan ini harus
tetap tampil di laporan dan di aplikasi.
"""

import numpy as np
import pandas as pd

from konstanta import BATAS_KELAS, RENTANG_AMAN

TEKSTUR = {"Lempung": 1.00, "Lempung Liat": 0.97, "Liat": 0.94}
KOMODITAS = ["Padi", "Jagung"]
KOREKSI_STATUS = [-0.20, -0.10, 0.00, 0.10, 0.20]


def status_faktor(nilai, batang):
    """Indeks status 0..4 (Sangat Rendah..Sangat Tinggi) terhadap batas kelas."""
    if nilai < batang[0]:
        return 0
    if nilai < batang[1]:
        return 1
    if nilai < batang[2]:
        return 2
    if nilai < batang[3]:
        return 3
    return 4


def dosis_ahli(baris):
    """Dosis rekomendasi 'pakar' (kg/ha) sebagai label satu baris data."""
    f_N = status_faktor(baris.N_persen, BATAS_KELAS["N_persen"])
    f_P = status_faktor(baris.P_ppm, BATAS_KELAS["P_ppm"])
    f_K = status_faktor(baris.K_me100g, BATAS_KELAS["K_me100g"])
    kom = baris.Komoditas

    if kom == "Padi":
        dasar = {"N": 200.0, "P": 75.0, "K": 50.0}
        efek_target = (baris.Target_Hasil - 5.0) / 1.0
    else:
        dasar = {"N": 275.0, "P": 140.0, "K": 70.0}
        efek_target = (baris.Target_Hasil - 6.0) / 1.5

    dN = dasar["N"] * (1 + KOREKSI_STATUS[f_N] + 0.05 * np.clip(efek_target, -2, 3))
    dP = dasar["P"] * (1 + KOREKSI_STATUS[f_P] + 0.05 * np.clip(efek_target, -2, 3))
    dK = dasar["K"] * (1 + KOREKSI_STATUS[f_K] + 0.04 * np.clip(efek_target, -2, 3))

    if baris.pH < 5.5:
        dP *= 1.15
        dN *= 1.05
    dN *= TEKSTUR[baris.Tekstur]
    dP *= TEKSTUR[baris.Tekstur]
    dK *= TEKSTUR[baris.Tekstur]
    if baris.Musim == "Hujan":
        dN *= 1.05

    n_lo, n_hi, p_lo, p_hi, k_lo, k_hi = RENTANG_AMAN[kom]
    dN = float(np.clip(dN, n_lo, n_hi))
    dP = float(np.clip(dP, p_lo, p_hi))
    dK = float(np.clip(dK, k_lo, k_hi))
    return pd.Series({"Dosis_N": dN, "Dosis_P": dP, "Dosis_K": dK})


def bangun_dataset(n=6000, seed=42):
    """Bangun dataset proxy n baris dengan label dosis dari logika tabel resmi."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "pH": rng.uniform(3.8, 8.2, n).round(2),
        "N_persen": rng.uniform(0.04, 1.10, n).round(3),
        "P_ppm": rng.uniform(2, 120, n).round(1),
        "K_me100g": rng.uniform(0.04, 1.20, n).round(3),
        "Tekstur": rng.choice(list(TEKSTUR), n, p=[0.45, 0.35, 0.20]),
        "Komoditas": rng.choice(KOMODITAS, n, p=[0.6, 0.4]),
        "Target_Hasil": np.nan,
        "Musim": rng.choice(["Hujan", "Kemarau"], n, p=[0.55, 0.45]),
    })
    padi = df.Komoditas == "Padi"
    df.loc[padi, "Target_Hasil"] = rng.uniform(4.0, 8.0, padi.sum()).round(1)
    df.loc[~padi, "Target_Hasil"] = rng.uniform(4.5, 10.5, (~padi).sum()).round(1)

    df = pd.concat([df, df.apply(dosis_ahli, axis=1)], axis=1)
    return df


FITUR = ["pH", "N_persen", "P_ppm", "K_me100g", "Tekstur", "Komoditas", "Target_Hasil", "Musim"]
KOLOM_X = [
    "pH", "N_persen", "P_ppm", "K_me100g", "Target_Hasil",
    "Tekstur_Lempung", "Tekstur_Lempung Liat", "Tekstur_Liat",
    "Komoditas_Padi", "Komoditas_Jagung",
    "Musim_Hujan", "Musim_Kemarau",
]


def susun_X(df):
    """One-hot encoding kategorikal, urutan kolom tetap untuk joblib."""
    X = pd.get_dummies(df[FITUR], columns=["Tekstur", "Komoditas", "Musim"], drop_first=False)
    return X[KOLOM_X]
