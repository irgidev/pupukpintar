# PupukPintar

Rekomendasi dosis pupuk N, P, K presisi per lahan untuk petani padi dan jagung di Bogor dan sekitarnya.

PupukPintar adalah proyek akhir mata kuliah Perancangan Produk Kecerdasan Buatan untuk Pertanian (PPKBP) Kelompok 14. Aplikasi ini lahir dari audit kami terhadap SAFRONS: aplikasi peta hara Bogor yang sepenuhnya deterministik dan berhenti pada saran pemupukan umum tanpa angka dosis. PupukPintar menutup celah itu dengan model machine learning yang memprediksi dosis N-P-K (kg/ha) spesifik per lahan, dilengkapi tingkat keyakinan, konversi kebutuhan pupuk per petak, estimasi biaya, pilihan paket sesuai modal, dan guardrail yang mengunci seluruh keluaran pada rentang aman tabel rekomendasi resmi (Permentan No. 40/2007 dan kaidah interpretasi Balittanah).

| | |
|---|---|
| Kelompok | 14 |
| Anggota | Irgi Setiawan (M0405241018), Syarif Abdullah Assagaf (M0405241033), Thogianna Anggitouli Metanoia Sinaga (M0405241077) |
| Fitur inti | Rekomendasi dosis NPK berbasis Random Forest dengan tingkat keyakinan, guardrail rentang aman, dan peta dengan alat gambar petak (luas terukur otomatis) di atas 191 area SAFRONS |
| Data latih | 6.000 baris proxy hasil ekstraksi logika tabel rekomendasi resmi |
| Kinerja model | Agreement 94,7 persen (uji silang 5-fold), 95,2 persen pada holdout 20 persen, latensi rata-rata 55 ms |

## Struktur repositori

```
pupukpintar/
├── app/
│   ├── backend/         server API, mesin rekomendasi, pelatihan model
│   │   ├── data_proxy.py    pembangun data latih proxy dari logika tabel resmi
│   │   ├── konstanta.py     rentang aman, batas kelas Balittanah, harga pupuk
│   │   ├── model.py         prediksi, keyakinan, guardrail, paket, penjelasan
│   │   ├── server.py        server HTTP (pustaka standar Python)
│   │   ├── train.py         pelatihan Random Forest dan penyimpanan metrik
│   │   ├── model.joblib     model terlatih (hasil train.py)
│   │   └── metrik_model.json metrik CV, holdout, feature importance
│   └── frontend/        antarmuka web mobile-first (HTML/CSS/JS murni)
├── poc/                 proof-of-concept LKP-P6 (skrip, notebook, grafik, hasil)
├── tests/               pengujian API + guardrail (pytest) dan perjalanan UI (Playwright)
├── docs/                wireframe, desain Figma (SVG), tangkapan layar, gambar laporan
├── laporan/             Laporan Akhir (docx) dan pembangkitnya
└── presentasi/          PPT Demo Day dan pembangkitnya
```

## Cara menjalankan

Kebutuhan: Python 3.12 atau lebih baru.

```bash
# 1) pasang dependensi
pip install -r app/backend/requirements.txt

# 2) latih model (sekali, menghasilkan model.joblib dan metrik_model.json)
cd app/backend
python train.py

# 3) jalankan server (port 8000 bawaan)
python server.py

# 4) buka aplikasi di browser
#    http://127.0.0.1:8000
```

## Menjalankan pengujian

```bash
# dari root repositori
python -m pytest tests/test_api.py -v          # 12 pengujian API dan guardrail

# perjalanan UI (butuh server hidup di port 8000 dan playwright chromium)
python tests/perjalanan_ui.py
```

## Kontrak API (POST /rekomendasi)

Masukan:

```json
{"pH": 5.8, "n_persen": 0.35, "p_ppm": 8.0, "k_me100g": 0.18,
 "tekstur": "Lempung", "komoditas": "Padi",
 "target_hasil_t_ha": 6.0, "luas_ha": 0.75, "musim": "Hujan"}
```

Keluaran (dipangkas):

```json
{"dosis_kg_ha": {"N": 207, "P": 71, "K": 51},
 "keyakinan": 0.84, "kategori_keyakinan": "sedang",
 "luar_sebaran_data_latih": false, "tampilkan_angka": true,
 "kebutuhan_petak_kg": {"Urea": 338, "SP36": 176, "KCl": 64},
 "estimasi_biaya_idr": 1242100,
 "paket": {"hemat": {...}, "standar": {...}, "optimal": {...}},
 "peringatan": ["Musim hujan: bagi pemupukan urea menjadi dua tahap agar nitrogen tidak tercuci."],
 "penjelasan": "Dosis N sedang karena stok nitrogen lahan Anda sedang. ...",
 "disclaimer": "Rekomendasi awal dari model, bukan pengganti uji tanah laboratorium. Verifikasi penyuluh sebelum pembelian pupuk."}
```

Guardrail: seluruh dosis dikunci pada rentang aman Permentan (padi N 150 sampai 250, P 50 sampai 100, K 25 sampai 75 kg/ha, jagung N 200 sampai 350, P 100 sampai 200, K 40 sampai 100). Input di luar sebaran data latih atau keyakinan di bawah 0,70 membuat sistem tidak menampilkan angka dan mengarahkan ke uji tanah laboratorium atau penyuluh.

## Batasan yang perlu diketahui

- Data latih adalah proxy hasil ekstraksi logika tabel resmi, bukan hasil uji tanah laboratorium. Validasi lapangan bersama poktan masih direncanakan.
- Peta wilayah memakai data spasial asli SAFRONS (191 area, audit LKP-P1). Petani dapat menggambar batas petaknya sendiri dan luas dihitung otomatis dari geometri (rumus Chamberlain-Duquette), nilai hara diambil dari unit SAFRONS tempat pusat petak berada. pH peta memakai nilai rata-rata area, band N-P-K dikonversi ke nilai perwakilan skala model (skrip app/frontend/data/gen_peta.py).
- Auth, penyimpanan server, dan panel penyuluh pada versi demo ini berjalan lokal di perangkat (localStorage).

## Lisensi

MIT. Lihat LICENSE.
