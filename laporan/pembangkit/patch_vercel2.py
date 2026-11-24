# -*- coding: utf-8 -*-
"""Patch: sisa tautan Vercel di PPT + rapikan kotak COBA SENDIRI slide 1
dan jarak sampul laporan."""

# ---------- PPT ----------
p = "presentasi/pembangkit/buat_ppt.py"
s = open(p, encoding="utf-8").read()

lama = '"Aplikasi: http://127.0.0.1:8000 (jalankan python server.py sesuai README)'
baru = '"Aplikasi: https://pupukpintar.vercel.app'
assert lama in s, "slide 1 aplikasi"
s = s.replace(lama, baru)

lama = '"Aplikasi demo: http://127.0.0.1:8000'
baru = '"Aplikasi demo: https://pupukpintar.vercel.app'
assert lama in s, "slide 10 aplikasi"
s = s.replace(lama, baru)

lama_kotak = "    kotak_teks(s, 1.12, 5.55, 6.9, 0.9,"
baru_kotak = "    kotak_teks(s, 1.12, 5.5, 6.9, 1.0,"
assert lama_kotak in s, "kotak slide 1"
s = s.replace(lama_kotak, baru_kotak)

open(p, "w", encoding="utf-8").write(s)
print("PPT: tautan Vercel + kotak rapi")

# ---------- laporan ----------
p2 = "laporan/pembangkit/buat_laporan.py"
s2 = open(p2, encoding="utf-8").read()
lama2 = '["Aplikasi berjalan", "Demo lokal http://127.0.0.1:8000, tanpa login, dijalankan dengan python server.py dari folder app/backend setelah train.py sekali dijalankan"]'
baru2 = '["Aplikasi berjalan", "https://pupukpintar.vercel.app, tanpa login. Versi lokal: jalankan python server.py dari folder app/backend setelah train.py sekali dijalankan"]'
assert lama2 in s2, "Bab 7.5"
s2 = s2.replace(lama2, baru2)

lama2b = '"app": "http://127.0.0.1:8000 (demo lokal, cara menjalankan ada di README repositori)",'
baru2b = '"app": "https://pupukpintar.vercel.app (deployment Vercel; versi lokal dijalankan lewat README)",'
assert lama2b in s2, "TAUTAN app"
s2 = s2.replace(lama2b, baru2b)

lama2c = '["Hosting", "Lokal untuk demo, rencana VPS kecil", "Belum ada akun hosting tim, biaya dihitung di Bab 9", "Vercel gratis (cocok statis, tetapi model Python butuh runtime server)"]'
baru2c = '["Hosting", "Demo lokal; deployment daring ke Vercel (subdomain pupukpintar.vercel.app)", "Subdomain ditetapkan sekarang agar tautan laporan dan presentasi konsisten saat deployment", "VPS kecil berbayar (dipakai bila butuh proses server persisten); Vercel gratis untuk demo daring"]'
assert lama2c in s2, "hosting row"
s2 = s2.replace(lama2c, baru2c)

# jarak sampul: lega antara nama -> logo -> prodi
lama_sp = 'baris_sampul("Thogianna Anggitouli Metanoia Sinaga - M0405241077", 12, False, 20)'
baru_sp = 'baris_sampul("Thogianna Anggitouli Metanoia Sinaga - M0405241077", 12, False, 30)'
assert lama_sp in s2
s2 = s2.replace(lama_sp, baru_sp)
lama_sp2 = 'par_logo.paragraph_format.space_after = Pt(20)'
baru_sp2 = 'par_logo.paragraph_format.space_after = Pt(30)'
assert lama_sp2 in s2
s2 = s2.replace(lama_sp2, baru_sp2)
lama_sp3 = 'baris_sampul("LAPORAN PROYEK PPKBP", 14, True, 10)'
baru_sp3 = 'baris_sampul("LAPORAN PROYEK PPKBP", 14, True, 14)'
assert lama_sp3 in s2
s2 = s2.replace(lama_sp3, baru_sp3)

open(p2, "w", encoding="utf-8").write(s2)
print("laporan: tautan Vercel + jarak sampul")

# ---------- README ----------
p3 = "README.md"
s3 = open(p3, encoding="utf-8").read()
if "pupukpintar.vercel.app" not in s3:
    s3 = s3.replace(
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |",
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |\n| Aplikasi (deployment Vercel) | https://pupukpintar.vercel.app |")
open(p3, "w", encoding="utf-8").write(s3)
print("README diperbarui")
