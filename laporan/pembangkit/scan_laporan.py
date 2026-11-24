# -*- coding: utf-8 -*-
"""
Pemindai halaman untuk daftar isi, daftar gambar, dan daftar tabel.

Membaca PDF hasil lintasan pertama, memetakan halaman fisik setiap judul
bab, subbab, daftar depan, dan caption, lalu menulis halaman_toi.json.
Dua angka di laporan memakai nomor halaman berjalan (arab) yang sama dengan
footer, sehingga daftar isi konsisten dengan halaman tercetak.

Jalankan setelah lintasan pertama (dari folder laporan):
    python pembangkit/scan_laporan.py
"""

import json
import re

import pymupdf

PDF = "Laporan_Akhir_PupukPintar_Kelompok14.pdf"
SUMBER = "pembangkit/buat_laporan.py"
KELUAR = "pembangkit/halaman_toi.json"

doc = pymupdf.open(PDF)
halaman = [doc[i].get_text() for i in range(doc.page_count)]
halaman_norm = [re.sub(r"\s+", " ", t) for t in halaman]

sumber = open(SUMBER, encoding="utf-8").read()

# ---------- judul tingkat 1 (14 pt) ----------
h1_list = re.findall(r'h1\("([^"]+)"\)', sumber) + re.findall(r'judul_depan\("([^"]+)"\)', sumber)
hasil_h1 = {}
for i in range(doc.page_count):
    d = doc[i].get_text("dict")
    for blok in d["blocks"]:
        for baris in blok.get("lines", []):
            ukuran_maks = max((span["size"] for span in baris["spans"]), default=0)
            teks_baris = "".join(span["text"] for span in baris["spans"]).strip()
            if ukuran_maks < 12.5 or not teks_baris:
                continue
            for t in h1_list:
                if teks_baris.upper() == t.upper() and t not in hasil_h1:
                    hasil_h1[t] = i + 1

# ---------- subbab (12 pt, menghindari halaman daftar) ----------
sub_sumber = re.findall(r'h2\("(\d+\.\d+ [^"]+)"\)', sumber)
sub_target = [re.sub(r"^(\d+\.\d+) ", r"\1. ", t).upper() for t in sub_sumber]
hasil_sub = {}
tabel_page = hasil_h1.get("Daftar Tabel") or 999
for i in range(doc.page_count):
    if i + 1 <= tabel_page:
        continue
    d = doc[i].get_text("dict")
    teks_hal = re.sub(r"\s+", " ", doc[i].get_text()).upper()
    for t in sub_target:
        if t in hasil_sub:
            continue
        ada = False
        for blok in d["blocks"]:
            for baris in blok.get("lines", []):
                for span in baris["spans"]:
                    if span["size"] >= 11.5 and span["text"].strip().upper() == t:
                        ada = True
                        break
                if ada:
                    break
            if ada:
                break
        if ada and t in teks_hal:
            hasil_sub[t] = i + 1

# ---------- caption gambar dan tabel (terjadi setelah daftar tabel selesai) ----------
batas_dt = hasil_h1.get("RINGKASAN EKSEKUTIF", 999)
cap_gambar = re.findall(r'"((?:Gambar) \d+\.\d+ [^"]*)"', sumber)
cap_tabel = re.findall(r'"((?:Tabel) [A-Z0-9]+\.\d+ [^"]*)"', sumber)
hasil_capg = {}
hasil_capt = {}
for cap in cap_gambar:
    norm_cap = re.sub(r"\s+", " ", cap)
    for i in range(doc.page_count):
        if i + 1 < batas_dt:
            continue
        if norm_cap in halaman_norm[i]:
            hasil_capg[norm_cap] = i + 1
            break
for cap in cap_tabel:
    norm_cap = re.sub(r"\s+", " ", cap)
    for i in range(doc.page_count):
        if i + 1 < batas_dt:
            continue
        if norm_cap in halaman_norm[i]:
            hasil_capt[norm_cap] = i + 1
            break

keluar = {
    "isi": hasil_h1.get("Daftar Isi"),
    "gambar": hasil_h1.get("Daftar Gambar"),
    "tabel": hasil_h1.get("Daftar Tabel"),
    "ringkasan": hasil_h1.get("RINGKASAN EKSEKUTIF"),
    "pustaka": hasil_h1.get("Daftar Pustaka"),
    "lampiran": hasil_h1.get("Lampiran"),
    "bab": {k: v for k, v in hasil_h1.items() if k.startswith("Bab ")},
    "sub": hasil_sub,
    "capg": hasil_capg,
    "capt": hasil_capt,
}

with open(KELUAR, "w", encoding="utf-8") as f:
    json.dump(keluar, f, ensure_ascii=False, indent=1, sort_keys=True)

hilang = [k for k, v in keluar.items() if v is None]
print("halaman total:", doc.page_count)
print("belum ketemu:", hilang if hilang else "tidak ada")
print("contoh:", {k: keluar[k] for k in list(keluar)[:8]})
