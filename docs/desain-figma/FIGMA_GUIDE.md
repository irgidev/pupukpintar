# Panduan Desain Figma PupukPintar

Berkas Figma utama proyek: https://www.figma.com/design/rSkPUlILq9yMteqXRwDBHF/PupukPintar?node-id=0-1
(berisi wireframe low-fidelity tiga layar dari LKP-P6). Berkas SVG pada folder ini adalah
kelanjutan high-fidelity dari wireframe tersebut.

## Isi folder

| Berkas | Isi |
|---|---|
| `layar-1-splash.svg` | Layar entry point: logo, tagline, kartu persetujuan data, tombol Masuk/Daftar |
| `layar-2-form-rekomendasi.svg` | Layar fitur AI utama: chip petak lahan, pemilih komoditas, target hasil, luas, musim |
| `layar-3-hasil.svg` | Layar hasil: badge keyakinan, tiga kartu dosis, kebutuhan per petak, estimasi biaya, paket, penjelasan, peringatan, disclaimer |
| `buat_desain_svg.py` | Pembangkit ketiga SVG (jalankan `python buat_desain_svg.py` untuk membuat ulang) |

## Cara memasukkan ke Figma

1. Buka berkas Figma PupukPintar di atas.
2. Seret ketiga berkas SVG langsung ke kanvas (Figma mengimpor SVG sebagai layer yang dapat diedit).
3. Letakkan di sebelah kanan wireframe low-fidelity pada frame yang sama, beri nama halaman "Hi-Fi".

## Token desain (sama dengan app/frontend/styles.css)

| Token | Nilai | Penggunaan |
|---|---|---|
| Hijau padi 700 | `#1E5B3F` | tombol utama, logo, menu aktif |
| Hijau padi 900 | `#143D2B` | judul layar, angka dosis |
| Hijau padi 100 | `#E4EEE6` | badge keyakinan tinggi, banner disclaimer |
| Kuning padi | `#F2C14E` | aksen logo, layar hasil alur kritis |
| Kuning padi muda | `#F9EED6` | peringatan dini, badge keyakinan sedang |
| Merah bata | `#A3352C` | keadaan bahaya, badge keyakinan rendah |
| Latar | `#F3F4EE` | latar layar |
| Garis | `#DCE0D6` | tepi kartu |
| Tinta | `#1D241F` | teks isi |
| Abu | `#55635A` | teks bantu |

Tipografi: Plus Jakarta Sans (400 teks isi, 600 menengah, 700 tombol dan label, 800 judul).
Font ini dipilih karena dirancang desainer Indonesia, dibaca nyaman untuk bahasa Indonesia
dan angka dosis, serta berlisensi terbuka.

Radius: kartu 10 px, tombol dan input 8 px, chip 22 px (bukan pil dekoratif, chip memang
pelabel status).

## Perubahan dari wireframe low-fidelity (alasannya tertulis di Bab 6.2 laporan)

1. Placeholder abu-abu diganti konten nyata: peta zona, chip lahan, kartu dosis berangka.
2. Badge keyakinan bergerak dari sebelah judul ke baris tersendiri agar tidak terpotong pada layar 390 px (temuan uji perjalanan UI).
3. Tiga kartu dosis diberi sub-label rentang aman resmi supaya angka selalu bisa dibandingkan pengguna.
4. Peringatan dini berbentuk pita kuning dengan ikon segitiga, terpisah dari penjelasan sederhana.
