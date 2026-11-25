# -*- coding: utf-8 -*-
"""Patch: URL Vercel konsisten + jarak sampul + kotak COBA SENDIRI rapi."""

# ---------- laporan ----------
p = "laporan/pembangkit/buat_laporan.py"
s = open(p, encoding="utf-8").read()
ganti = [
    ('"app": "http://127.0.0.1:8000 (demo lokal, cara menjalankan ada di README repositori)",',
     '"app": "https://pupukpintar.vercel.app (deployment Vercel; versi lokal dijalankan lewat README)",'),
    ('["Aplikasi berjalan", "Demo lokal http://127.0.0.1:8000, tanpa login, dijalankan dengan python server.py dari folder app/backend setelah train.py sekali dijalankan"]',
     '["Aplikasi berjalan", "https://pupukpintar.vercel.app, tanpa login. Versi lokal: jalankan python server.py dari folder app/backend setelah train.py sekali dijalankan"]'),
    ('["Hosting", "Lokal untuk demo, rencana VPS kecil", "Belum ada akun hosting tim, biaya dihitung di Bab 9", "Vercel gratis (cocok statis, tetapi model Python butuh runtime server)"]',
     '["Hosting", "Demo lokal; deployment daring ke Vercel (subdomain pupukpintar.vercel.app)", "Subdomain ditetapkan sekarang agar tautan laporan dan presentasi konsisten saat deployment", "VPS kecil berbayar (dipakai bila butuh proses server persisten); Vercel gratis untuk demo daring"]'),
    ('baris_sampul("Thogianna Anggitouli Metanoia Sinaga - M0405241077", 12, False, 20)',
     'baris_sampul("Thogianna Anggitouli Metanoia Sinaga - M0405241077", 12, False, 30)'),
    ('par_logo.paragraph_format.space_after = Pt(20)',
     'par_logo.paragraph_format.space_after = Pt(30)'),
    ('baris_sampul("LAPORAN PROYEK PPKBP", 14, True, 10)',
     'baris_sampul("LAPORAN PROYEK PPKBP", 14, True, 14)'),
]
for lama, baru in ganti:
    if lama in s:
        s = s.replace(lama, baru)
        print("laporan OK:", baru[:60])
    else:
        print("laporan: sudah diterapkan / tidak ada:", lama[:50])
open(p, "w", encoding="utf-8").write(s)

# ---------- PPT ----------
p2 = "presentasi/pembangkit/buat_ppt.py"
s2 = open(p2, encoding="utf-8").read()
g2 = [
    ('"Aplikasi: http://127.0.0.1:8000 (jalankan python server.py sesuai README)',
     '"Aplikasi: https://pupukpintar.vercel.app'),
    ('"Aplikasi demo: http://127.0.0.1:8000',
     '"Aplikasi demo: https://pupukpintar.vercel.app'),
    ("    kotak_teks(s, 1.12, 5.55, 6.9, 0.9,",
     "    kotak_teks(s, 1.12, 5.5, 6.9, 1.0,"),
]
for lama, baru in g2:
    if lama in s2:
        s2 = s2.replace(lama, baru)
        print("PPT OK:", baru[:60])
    else:
        print("PPT: sudah diterapkan / tidak ada:", lama[:50])
open(p2, "w", encoding="utf-8").write(s2)

# ---------- README ----------
p3 = "README.md"
s3 = open(p3, encoding="utf-8").read()
if "pupukpintar.vercel.app" not in s3:
    s3 = s3.replace(
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |",
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |\n| Aplikasi (deployment Vercel) | https://pupukpintar.vercel.app |")
    print("README: baris Vercel ditambahkan")
else:
    print("README sudah memuat Vercel")
open(p3, "w", encoding="utf-8").write(s3)
