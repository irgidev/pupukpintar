# -*- coding: utf-8 -*-
"""Patch: URL Vercel, jarak sampul, dan sinkron hosting."""

# ---------- laporan ----------
p = "laporan/pembangkit/buat_laporan.py"
s = open(p, encoding="utf-8").read()
ganti = [
    # tautan aplikasi memakai domain Vercel
    ('"app": "http://127.0.0.1:8000 (demo lokal, cara menjalankan ada di README repositori)",',
     '"app": "https://pupukpintar.vercel.app (deployment Vercel; cara menjalankan versi lokal ada di README repositori)",'),
    # Bab 7.5 baris aplikasi berjalan
    ('["Aplikasi berjalan", "Demo lokal http://127.0.0.1:8000, tanpa login, dijalankan dengan python server.py dari folder app/backend setelah train.py sekali dijalankan"]',
     '["Aplikasi berjalan", "https://pupukpintar.vercel.app, tanpa login. Versi lokal: jalankan python server.py dari folder app/backend setelah train.py sekali dijalankan"]'),
    # Bab 7.1 baris hosting
    ('["Hosting", "Lokal untuk demo, rencana VPS kecil", "Belum ada akun hosting tim, biaya dihitung di Bab 9", "Vercel gratis (cocok statis, tetapi model Python butuh runtime server)"]',
     '["Hosting", "Deployment ke Vercel pada subdomain pupukpintar.vercel.app; pengembangan harian tetap lokal", "Subdomain sudah ditetapkan sekarang agar tautan laporan dan presentasi konsisten saat deployment", "VPS kecil berbayar (dipakai bila butuh proses server persisten); Vercel gratis dipakai untuk demo daring"]'),
]
for lama, baru in ganti:
    assert lama in s, "TIDAK KETEMU: " + lama[:60]
    s = s.replace(lama, baru)

# catatan hosting pada Bab 9 (asumsi tetap VPS sebagai model biaya konservatif)
lama9 = 'ditetapkan sebagai asumsi tim karena belum ada akun hosting). Belum ada tagihan nyata karena demo berjalan lokal'
baru9 = 'ditetapkan sebagai asumsi tim). Alternatif gratis: Vercel Hobby untuk demo daring. Belum ada tagihan nyata karena demo berjalan lokal'
assert lama9 in s
s = s.replace(lama9, baru9)
open(p, "w", encoding="utf-8").write(s)
print("laporan: URL Vercel + hosting disinkronkan")

# ---------- PPT ----------
p2 = "presentasi/pembangkit/buat_ppt.py"
s2 = open(p2, encoding="utf-8").read()
g2 = [
    # slide 1: aplikasi memakai domain Vercel
    ('"Aplikasi: http://127.0.0.1:8000 (jalankan python server.py sesuai README)\\n"',
     '"Aplikasi: https://pupukpintar.vercel.app\\n"'),
    # slide 10: aplikasi memakai domain Vercel
    ('"Aplikasi demo: http://127.0.0.1:8000\\nVideo: drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1",',
     '"Aplikasi demo: https://pupukpintar.vercel.app\\nVideo: drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1",'),
]
for lama, baru in g2:
    assert lama in s2, "PPT TIDAK KETEMU: " + lama[:60]
    s2 = s2.replace(lama, baru)

# rapikan kotak COBA SENDIRI slide 1: kotak lebih tinggi, teks mulai lebih atas
lama_kotak1 = '''    kotak_teks(s, 1.12, 5.55, 6.9, 0.9,'''
baru_kotak1 = '''    kotak_teks(s, 1.12, 5.5, 6.9, 1.0,'''
assert lama_kotak1 in s2
s2 = s2.replace(lama_kotak1, baru_kotak1)
# baris video slide 1 pindah ke baris sendiri agar rapi (sudah \n terpisah)
open(p2, "w", encoding="utf-8").write(s2)
print("PPT: tautan Vercel + kotak slide 1 dirapikan")

# ---------- README ----------
p3 = "README.md"
s3 = open(p3, encoding="utf-8").read()
if "pupukpintar.vercel.app" not in s3:
    s3 = s3.replace(
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |",
        "| Video demo | https://drive.google.com/drive/folders/1hZzJHdhQZEa4-a4qC8jQDy1sYrweZVA1 |\n| Aplikasi (deployment Vercel) | https://pupukpintar.vercel.app |")
open(p3, "w", encoding="utf-8").write(s3)
print("README diperbarui")
