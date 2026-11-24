# -*- coding: utf-8 -*-
"""
Konstanta domain PupukPintar.

Semua angka di berkas ini adalah batas dan harga yang dirujuk di laporan akhir.
Perubahan nilai di sini otomatis dipakai model, API, dan uji.
"""

# Rentang aman dosis hara (kg/ha) dari tabel rekomendasi pemupukan resmi
# Permentan No. 40/2007 (anjuran umum pemupukan berimbang padi dan jagung).
# Urutan nilai: N_min, N_max, P_min, P_max, K_min, K_max.
RENTANG_AMAN = {
    "Padi": (150.0, 250.0, 50.0, 100.0, 25.0, 75.0),
    "Jagung": (200.0, 350.0, 100.0, 200.0, 40.0, 100.0),
}

# Batas kelas interpretasi kesuburan tanah mengikuti kaidah Balittanah
# (memetakan nilai hasil uji tanah ke status Sangat Rendah sampai Tinggi).
BATAS_KELAS = {
    "N_persen": [0.10, 0.21, 0.40, 0.60],
    "P_ppm": [5.0, 11.0, 26.0, 60.0],
    "K_me100g": [0.10, 0.21, 0.41, 0.80],
}

LABEL_STATUS = ["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]

# Asumsi harga pupuk (Rp per kg) yang dipakai estimasi biaya.
# Urea dan SP-36 mengikuti HET pupuk bersubsidi penetapan RDKK Kementan
# (asumsi tim, nilai umum 2024). KCl bukan pupuk subsidi sehingga memakai
# harga pasar pengecer lokal (asumsi tim).
HARGA_PUPUK_IDR_PER_KG = {
    "Urea": 2250,
    "SP36": 2300,
    "KCl": 5000,
}

# Pemetaan dosis unsur hara (kg/ha) menjadi jenis pupuk niaga.
# Angka kadar unsur: Urea 46% N, SP-36 ~30% P2O5, KCl ~60% K2O.
KADAR_UNSUR = {
    "Urea": 0.46,
    "SP36": 0.30,
    "KCl": 0.60,
}

# Ambang keyakinan untuk kategori tampilan (Bab 6.4 laporan).
AMBAK_YAKIN = 0.85      # >= AMBAK_YAKIN              -> Keyakinan tinggi
AMBAK_RAGU = 0.70       # AMBAK_RAGU..AMBAK_YAKIN     -> Keyakinan sedang
                        # < AMBAK_RAGU atau luar sebaran -> Tidak yakin

# Rentang layak input (di luar rentang ini ditolak sebagai input buruk).
BATAS_INPUT = {
    "pH": (3.0, 9.0),
    "n_persen": (0.01, 2.0),
    "p_ppm": (1.0, 200.0),
    "k_me100g": (0.01, 2.5),
    "target_hasil_t_ha": {"Padi": (3.0, 10.0), "Jagung": (3.0, 13.0)},
    "luas_ha": (0.05, 10.0),
}

# Rentang sebaran data latih (input di luar ini ditandai luar sebaran dan
# sistem tidak memaksakan angka, melainkan mengarahkan ke uji lab/penyuluh).
SEBARAN_DATA_LATIH = {
    "pH": (3.8, 8.2),
    "p_ppm": (2.0, 120.0),
    "k_me100g": (0.04, 1.20),
    "n_persen": (0.04, 1.10),
    "target_hasil_t_ha": {"Padi": (4.0, 8.0), "Jagung": (4.5, 10.5)},
}

TEKSTUR_TANAH = ["Lempung", "Lempung Liat", "Liat"]

DISCLAIMER = (
    "Rekomendasi awal dari model, bukan pengganti uji tanah laboratorium. "
    "Verifikasi penyuluh sebelum pembelian pupuk."
)
