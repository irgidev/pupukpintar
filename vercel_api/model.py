# -*- coding: utf-8 -*-
"""
Mesin rekomendasi PupukPintar: prediksi dosis N-P-K, keyakinan, guardrail,
peringatan rule-based, konversi kebutuhan pupuk per petak, estimasi biaya,
paket sesuai modal, dan penjelasan bahasa sederhana.

Semua keluaran dikunci pada rentang aman tabel resmi (konstanta.py).
"""

import json
import math
import os

import joblib
import numpy as np

from konstanta import (
    AMBAK_RAGU,
    AMBAK_YAKIN,
    BATAS_INPUT,
    BATAS_KELAS,
    DISCLAIMER,
    HARGA_PUPUK_IDR_PER_KG,
    KADAR_UNSUR,
    LABEL_STATUS,
    RENTANG_AMAN,
    SEBARAN_DATA_LATIH,
)

# Urutan kolom harus sama dengan KOLOM_X pada data_proxy; dideklarasikan lokal
# agar inferensi tersaji tidak bergantung pada modul pelatihan data.
KOLOM_X = [
    "pH", "N_persen", "P_ppm", "K_me100g", "Target_Hasil",
    "Tekstur_Lempung", "Tekstur_Lempung Liat", "Tekstur_Liat",
    "Komoditas_Padi", "Komoditas_Jagung",
    "Musim_Hujan", "Musim_Kemarau",
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
METRIK_PATH = os.path.join(os.path.dirname(__file__), "metrik_model.json")

_model = None


def muat_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def baca_metrik():
    with open(METRIK_PATH, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------
# Validasi input
# ----------------------------------------------------------------------

def validasi(payload):
    """Kembalikan daftar pesan galat input buruk. Kosong berarti layak."""
    galat = []
    for kolom in ("pH", "n_persen", "p_ppm", "k_me100g", "target_hasil_t_ha", "luas_ha"):
        v = payload.get(kolom)
        if v is None or not isinstance(v, (int, float)) or isinstance(v, bool) or math.isnan(v):
            galat.append(f"{kolom} wajib berupa angka")
    if galat:
        return galat

    for kolom, (lo, hi) in BATAS_INPUT.items():
        if kolom == "target_hasil_t_ha":
            kom = payload.get("komoditas")
            if kom not in ("Padi", "Jagung"):
                galat.append("komoditas harus 'Padi' atau 'Jagung'")
                continue
            lo, hi = BATAS_INPUT[kolom][kom]
        v = float(payload[kolom])
        if v < lo or v > hi:
            galat.append(f"{kolom}={v} di luar rentang layak {lo} sampai {hi}")

    if payload.get("tekstur") not in ("Lempung", "Lempung Liat", "Liat"):
        galat.append("tekstur harus Lempung, Lempung Liat, atau Liat")
    if payload.get("musim") not in ("Hujan", "Kemarau"):
        galat.append("musim harus 'Hujan' atau 'Kemarau'")
    return galat


def luar_sebaran(payload):
    """True bila input di luar sebaran data latih (kasus meragukan)."""
    cek = [
        not (SEBARAN_DATA_LATIH["pH"][0] <= payload["pH"] <= SEBARAN_DATA_LATIH["pH"][1]),
        not (SEBARAN_DATA_LATIH["n_persen"][0] <= payload["n_persen"] <= SEBARAN_DATA_LATIH["n_persen"][1]),
        not (SEBARAN_DATA_LATIH["p_ppm"][0] <= payload["p_ppm"] <= SEBARAN_DATA_LATIH["p_ppm"][1]),
        not (SEBARAN_DATA_LATIH["k_me100g"][0] <= payload["k_me100g"] <= SEBARAN_DATA_LATIH["k_me100g"][1]),
    ]
    lo, hi = SEBARAN_DATA_LATIH["target_hasil_t_ha"][payload["komoditas"]]
    cek.append(not (lo <= payload["target_hasil_t_ha"] <= hi))
    return any(cek)


# ----------------------------------------------------------------------
# Prediksi dan keyakinan
# ----------------------------------------------------------------------

def prediksi(payload):
    """Prediksi dosis (kg/ha), keyakinan, dan sebaran prediksi antarpohon."""
    model = muat_model()
    baris = {
        "pH": payload["pH"], "N_persen": payload["n_persen"], "P_ppm": payload["p_ppm"],
        "K_me100g": payload["k_me100g"], "Target_Hasil": payload["target_hasil_t_ha"],
        "Tekstur_Lempung": 0, "Tekstur_Lempung Liat": 0, "Tekstur_Liat": 0,
        "Komoditas_Padi": 0, "Komoditas_Jagung": 0,
        "Musim_Hujan": 0, "Musim_Kemarau": 0,
    }
    baris[f"Tekstur_{payload['tekstur']}"] = 1
    baris[f"Komoditas_{payload['komoditas']}"] = 1
    baris[f"Musim_{payload['musim']}"] = 1
    X = np.array([[baris[k] for k in KOLOM_X]], dtype=float)

    dosis = model.predict(X)[0]
    pohon = np.stack([est.predict(X)[0] for est in model.estimators_])
    cv_relatif = float((pohon.std(axis=0) / np.maximum(pohon.mean(axis=0), 1e-9)).mean())
    keyakinan = float(max(0.0, min(1.0, 1 - cv_relatif * 2)))
    return dosis, keyakinan


# ----------------------------------------------------------------------
# Status hara dan peringatan rule-based
# ----------------------------------------------------------------------

def status_hara(payload):
    status = {}
    peta = {"N": ("n_persen", "N_persen"), "P": ("p_ppm", "P_ppm"), "K": ("k_me100g", "K_me100g")}
    for unsur, (kolom_in, kolom_batas) in peta.items():
        idx = next((i for i, b in enumerate(BATAS_KELAS[kolom_batas]) if payload[kolom_in] < b), 4)
        status[unsur] = LABEL_STATUS[idx]
    return status


def peringatan_rule(payload, status):
    pesan = []
    if payload["pH"] < 4.5:
        pesan.append("Tanah sangat masam (pH {pH}). Pemupukan P tidak efektif sebelum pengapuran. Konsultasikan pengapuran ke penyuluh.".format(pH=f"{payload['pH']:.1f}".replace(".", ",")))
    elif payload["pH"] < 5.5:
        pesan.append("Tanah masam (pH {pH}). Pertimbangkan pengapuran karena fosfor mudah terikat.".format(pH=f"{payload['pH']:.1f}".replace(".", ",")))
    if status["P"] in ("Sangat Tinggi",):
        pesan.append("Stok P sudah sangat tinggi. Dosis P dijaga minimum, jangan menambah SP-36.")
    if status["K"] in ("Sangat Tinggi",):
        pesan.append("Stok K sudah sangat tinggi. Dosis K dijaga minimum.")
    if payload["musim"] == "Hujan":
        pesan.append("Musim hujan: bagi pemupukan urea menjadi dua tahap agar nitrogen tidak tercuci.")
    return pesan


# ----------------------------------------------------------------------
# Konversi kebutuhan pupuk niaga, biaya, dan paket
# ----------------------------------------------------------------------

def kebutuhan_petak(dosis, luas_ha):
    """Konversi dosis unsur (kg/ha) menjadi kg pupuk niaga per petak."""
    return {
        "Urea": round(dosis[0] * luas_ha / KADAR_UNSUR["Urea"]),
        "SP36": round(dosis[1] * luas_ha / KADAR_UNSUR["SP36"]),
        "KCl": round(dosis[2] * luas_ha / KADAR_UNSUR["KCl"]),
    }


def biaya(kebutuhan):
    return int(round(sum(kebutuhan[p] * HARGA_PUPUK_IDR_PER_KG[p] for p in kebutuhan)))


def susun_paket(dosis, komoditas, luas_ha):
    lo, hi = RENTANG_AMAN[komoditas][0::2], RENTANG_AMAN[komoditas][1::2]
    faktor = {"hemat": 0.85, "standar": 1.00, "optimal": 1.10}
    hasil = {}
    for nama, f in faktor.items():
        d = [
            float(np.clip(dosis[i] * f, lo[i], hi[i]))
            for i in range(3)
        ]
        keb = kebutuhan_petak(d, luas_ha)
        hasil[nama] = {
            "dosis_kg_ha": {h: round(v) for h, v in zip(("N", "P", "K"), d)},
            "kebutuhan_petak_kg": keb,
            "estimasi_biaya_idr": biaya(keb),
            "catatan": {
                "hemat": "Untuk modal terbatas. Dosis 85% dari standar, risiko hasil sedikit di bawah optimal.",
                "standar": "Dosis penuh sesuai rekomendasi model untuk target hasil Anda.",
                "optimal": "Dosis 110% (dalam rentang aman) untuk mengejar target hasil maksimal.",
            }[nama],
        }
    return hasil


# ----------------------------------------------------------------------
# Penjelasan bahasa sederhana (rule-based template, bukan LLM)
# ----------------------------------------------------------------------

def penjelasan(payload, status, dosis):
    kalimat = []
    sN, sP, sK = status["N"], status["P"], status["K"]
    if sN in ("Sangat Rendah", "Rendah"):
        kalimat.append("Dosis N tinggi karena stok nitrogen lahan Anda " + sN.lower() + ".")
    elif sN in ("Tinggi", "Sangat Tinggi"):
        kalimat.append("Dosis N diturunkan karena stok nitrogen lahan Anda " + sN.lower() + ".")
    else:
        kalimat.append("Dosis N sedang karena stok nitrogen lahan Anda sedang.")

    if payload["pH"] < 5.5:
        kalimat.append("P dinaikkan karena tanah masam sehingga fosfor mudah terikat.")
    elif sP in ("Tinggi", "Sangat Tinggi"):
        kalimat.append("P dijaga rendah karena stok fosfor lahan sudah " + sP.lower() + ".")
    else:
        kalimat.append("P menyesuaikan stok fosfor lahan yang " + sP.lower() + ".")

    if sK in ("Tinggi", "Sangat Tinggi"):
        kalimat.append("K cukup, jadi dosisnya dijaga rendah.")
    elif sK in ("Sangat Rendah", "Rendah"):
        kalimat.append("K dinaikkan karena stok kalium lahan " + sK.lower() + ".")
    else:
        kalimat.append("K menyesuaikan stok kalium lahan yang sedang.")

    kalimat.append(f"Target hasil {str(payload['target_hasil_t_ha']).replace('.', ',')} ton/ha untuk {payload['komoditas'].lower()} juga ikut menaikkan kebutuhan hara.")
    return " ".join(kalimat)


# ----------------------------------------------------------------------
# Titik masuk utama
# ----------------------------------------------------------------------

def buat_rekomendasi(payload):
    """
    payload (bersih, sudah lolos validasi):
        pH, n_persen, p_ppm, k_me100g, tekstur, komoditas,
        target_hasil_t_ha, luas_ha, musim
    """
    komoditas = payload["komoditas"]
    status = status_hara(payload)
    luar = luar_sebaran(payload)
    dosis, keyakinan = prediksi(payload)

    lo, hi = RENTANG_AMAN[komoditas][0::2], RENTANG_AMAN[komoditas][1::2]
    # dibulatkan ke kg/ha utuh sejak awal agar semua turunan (kebutuhan petak,
    # paket, biaya) bisa dihitung ulang petani dari angka yang ditampilkan
    dosis_aman = [float(round(float(np.clip(dosis[i], lo[i], hi[i])))) for i in range(3)]

    kategori = ("tinggi" if keyakinan >= AMBAK_YAKIN else "sedang" if keyakinan >= AMBAK_RAGU else "rendah")
    tampil_angka = kategori in ("tinggi", "sedang") and not luar

    hasil = {
        "masukan": {
            "pH": payload["pH"], "n_persen": payload["n_persen"], "p_ppm": payload["p_ppm"],
            "k_me100g": payload["k_me100g"], "tekstur": payload["tekstur"],
            "komoditas": komoditas, "target_hasil_t_ha": payload["target_hasil_t_ha"],
            "luas_ha": payload["luas_ha"], "musim": payload["musim"],
        },
        "status_hara": status,
        "keyakinan": round(keyakinan, 2),
        "kategori_keyakinan": kategori,
        "luar_sebaran_data_latih": luar,
        "tampilkan_angka": tampil_angka,
        "dosis_kg_ha": {h: round(v) for h, v in zip(("N", "P", "K"), dosis_aman)} if tampil_angka else None,
        "rentang_aman_kg_ha": {
            "N": [lo[0], hi[0]], "P": [lo[1], hi[1]], "K": [lo[2], hi[2]],
        },
        "peringatan": peringatan_rule(payload, status),
        "penjelasan": penjelasan(payload, status, dosis_aman),
        "disclaimer": DISCLAIMER,
    }

    if tampil_angka:
        paket = susun_paket(dosis_aman, komoditas, payload["luas_ha"])
        hasil["paket"] = paket
        keb = kebutuhan_petak(dosis_aman, payload["luas_ha"])
        hasil["kebutuhan_petak_kg"] = keb
        hasil["estimasi_biaya_idr"] = biaya(keb)
    else:
        hasil["paket"] = None
        hasil["kebutuhan_petak_kg"] = None
        hasil["estimasi_biaya_idr"] = None
        if luar:
            hasil["peringatan"].insert(0, "Kondisi lahan di luar sebaran data latih. Sistem tidak menampilkan angka. Sebaiknya lakukan uji tanah laboratorium.")
        else:
            hasil["peringatan"].insert(0, "Model belum cukup yakin untuk kasus ini. Angka tidak ditampilkan agar tidak salah langkah.")
    return hasil
