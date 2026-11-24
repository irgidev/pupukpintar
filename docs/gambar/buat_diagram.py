# -*- coding: utf-8 -*-
"""
Pembangkit gambar laporan: sitemap, arsitektur sistem, pipeline data,
dan feature importance.

Jalankan dari folder docs/gambar:
    python buat_diagram.py
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HIJAU = "#1E5B3F"
HIJAU_MUDA = "#E4EEE6"
KUNING = "#F2C14E"
TINTA = "#1D241F"
ABU = "#5C6B63"
GARIS = "#B9C4BB"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
})


def kotak(ax, x, y, w, h, teks, fc="#FFFFFF", ec=GARIS, lw=1.4, fs=10, tebal=400, tc=TINTA, radius=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0.004,rounding_size={radius}",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, teks, ha="center", va="center",
            fontsize=fs, color=tc, fontweight=tebal, linespacing=1.35)


def panah(ax, x1, y1, x2, y2, warna=ABU, lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle="-|>", mutation_scale=14,
                                 color=warna, lw=lw, shrinkA=2, shrinkB=2))


def simpan(fig, nama):
    fig.savefig(nama, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("tersimpan:", nama)


# ----------------------------------------------------------------------
# 1) SITEMAP
# ----------------------------------------------------------------------
def sitemap():
    fig, ax = plt.subplots(figsize=(10.4, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.6)
    ax.axis("off")

    kotak(ax, 3.3, 5.85, 3.4, 0.6, "Splash, Onboarding,\nPersetujuan Data", fc=HIJAU, ec=HIJAU, tc="white", fs=9.5, tebal="bold")
    kotak(ax, 3.6, 4.85, 2.8, 0.5, "Beranda (Dashboard)", fc=HIJAU_MUDA, ec=HIJAU, fs=10, tebal="bold")

    panah(ax, 5.0, 5.85, 5.0, 5.38)

    menu = [
        (0.15, "Lahan Saya"),
        (2.65, "Rekomendasi Dosis\n(fitur AI utama)"),
        (5.15, "Papan Penyuluhan"),
        (7.65, "Profil dan\nPengaturan"),
    ]
    sub = [
        "Daftar petak\nTambah: peta atau uji tanah\nDetail kondisi hara",
        "Formulir komoditas dan target\nHasil dosis, keyakinan, paket\nRiwayat rekomendasi",
        "Tips pemupukan\nVerifikasi penyuluh\nKontak penyuluh",
        "Akun dan persetujuan\nOpsi pelatihan model\nHapus data",
    ]
    for (x, judul), isi in zip(menu, sub):
        panah(ax, 5.0, 4.85, x + 1.1, 4.32)
        kotak(ax, x, 3.7, 2.2, 0.62, judul, fc="white", ec=HIJAU, fs=8.6, tebal="bold")
        kotak(ax, x, 2.3, 2.2, 1.1, isi, fc="#FBFCFA", ec=GARIS, fs=8.0, tc=ABU)

    kotak(ax, 2.75, 1.15, 2.0, 0.62, "Hasil: dosis, keyakinan,\nbiaya, paket", fc=KUNING, ec=KUNING, tc=TINTA, fs=8.4, tebal="bold")
    panah(ax, 3.75, 2.3, 3.75, 1.8)
    ax.text(5.1, 0.7, "Alur kritis: pilih petak → pilih komoditas → Hitung Rekomendasi (3 ketukan dari beranda)",
            ha="center", fontsize=9, color=HIJAU, fontweight="bold")

    simpan(fig, "sitemap.png")


# ----------------------------------------------------------------------
# 2) ARSITEKTUR SISTEM
# ----------------------------------------------------------------------
def arsitektur():
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    kotak(ax, 0.3, 3.4, 2.5, 1.9,
          "Antarmuka web\n(HTML/CSS/JS murni)\n5 layar utama\nstate di localStorage",
          fc=HIJAU_MUDA, ec=HIJAU, fs=9)
    kotak(ax, 3.55, 4.35, 2.6, 0.95, "POST /rekomendasi\n(input 9 field, kontrak JSON)", fc="white", ec=GARIS, fs=8.6)
    kotak(ax, 3.55, 3.3, 2.6, 0.8, "GET /model/info, /api/zona", fc="white", ec=GARIS, fs=8.6)
    kotak(ax, 3.55, 2.3, 2.6, 0.8, "GET / (berkas statis)", fc="white", ec=GARIS, fs=8.6)
    panah(ax, 2.8, 4.5, 3.55, 4.6)
    panah(ax, 2.8, 4.1, 3.55, 3.7)
    panah(ax, 2.8, 3.6, 3.55, 2.7)

    kotak(ax, 6.9, 3.05, 2.8, 2.25,
          "Server (http.server)\nvalidasi input\npanggil mesin rekomendasi\nsusun JSON jawaban",
          fc=HIJAU, ec=HIJAU, tc="white", fs=9)
    panah(ax, 6.15, 4.6, 6.9, 4.3)
    panah(ax, 6.15, 3.7, 6.9, 3.9)
    panah(ax, 6.15, 2.7, 6.9, 3.2)

    kotak(ax, 6.9, 0.9, 2.8, 1.7,
          "Mesin rekomendasi\nRandom Forest (joblib)\n+ keyakinan antarpohon\n+ guardrail rentang resmi\n+ aturan Balittanah",
          fc="#FBFCFA", ec=HIJAU, fs=8.6)
    panah(ax, 8.3, 3.05, 8.3, 2.6)

    kotak(ax, 0.3, 0.9, 2.5, 1.7,
          "Data latih\n6.000 baris proxy\n(logika tabel Permentan\n40/2007 + Balittanah)\ntrain.py -> model.joblib",
          fc="#FBFCFA", ec=GARIS, fs=8.6, tc=ABU)
    panah(ax, 2.8, 1.7, 6.9, 1.55, warna=ABU, lw=1.3)

    ax.text(5.0, 0.35, "Data uji pengujian dipisahkan dari data latih (holdout 20 persen, seed berbeda)",
            ha="center", fontsize=8.6, color=ABU)

    simpan(fig, "arsitektur.png")


# ----------------------------------------------------------------------
# 3) PIPELINE DATA
# ----------------------------------------------------------------------
def pipeline():
    fig, ax = plt.subplots(figsize=(9.6, 3.1))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.3)
    ax.axis("off")

    langkah = [
        ("Tabel resmi\nPermentan 40/2007\ndan kaidah Balittanah", "white"),
        ("Ekstraksi aturan\nke fungsi dosis pakar\n(semi-automated)", "white"),
        ("Sampling 6.000 baris\n8 fitur + 3 label\n(seed 42)", HIJAU_MUDA),
        ("Pemisahan data\nCV 5-fold dan\nholdout 20 persen", "white"),
        ("Pelatihan Random Forest\nevaluasi agreement,\nR2, MAE", HIJAU_MUDA),
        ("Ekspor model.joblib\ndan metrik_model.json\nke server", "white"),
    ]
    x = 0.15
    w = 1.42
    for i, (teks, fc) in enumerate(langkah):
        kotak(ax, x, 0.7, w, 1.2, teks, fc=fc, ec=HIJAU if fc != "white" else GARIS, fs=7.6)
        if i < len(langkah) - 1:
            panah(ax, x + w + 0.02, 1.3, x + w + 0.16, 1.3, lw=1.3)
        x += w + 0.18

    ax.text(5.0, 0.25, "Prinsip: label berasal dari logika tabel resmi, bukan dari pengarangan angka (strategi pelabelan semi-automated LKP-P4)",
            ha="center", fontsize=8.4, color=ABU)

    simpan(fig, "pipeline_data.png")


# ----------------------------------------------------------------------
# 4) FEATURE IMPORTANCE
# ----------------------------------------------------------------------
def feature_importance():
    with open(os.path.join("..", "..", "app", "backend", "metrik_model.json"), encoding="utf-8") as f:
        metrik = json.load(f)
    fi = metrik["feature_importance"]
    peta_label = {
        "pH": "pH tanah", "N_persen": "N (%)", "P_ppm": "P (ppm)", "K_me100g": "K (me/100g)",
        "Target_Hasil": "Target hasil", "Komoditas_Padi": "Komoditas: padi",
        "Komoditas_Jagung": "Komoditas: jagung", "Tekstur_Lempung": "Tekstur: lempung",
        "Tekstur_Lempung Liat": "Tekstur: lempung liat", "Tekstur_Liat": "Tekstur: liat",
        "Musim_Hujan": "Musim: hujan", "Musim_Kemarau": "Musim: kemarau",
    }
    pasangan = sorted(fi.items(), key=lambda t: t[1])
    label = [peta_label.get(k, k) for k, _ in pasangan]
    nilai = [v for _, v in pasangan]

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    batang = ax.barh(label, nilai, color=HIJAU, height=0.62)
    ax.set_xlabel("Pentingnya fitur (mean decrease in impurity)")
    for b, v in zip(batang, nilai):
        ax.text(v + 0.004, b.get_y() + b.get_height() / 2, f"{v:.3f}", va="center", fontsize=8.5, color=TINTA)
    ax.set_xlim(0, max(nilai) * 1.18)
    ax.tick_params(axis="y", labelsize=9)
    fig.tight_layout()
    simpan(fig, "feature_importance.png")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sitemap()
    arsitektur()
    pipeline()
    feature_importance()
