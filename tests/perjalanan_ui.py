# -*- coding: utf-8 -*-
"""
Perjalanan UI PupukPintar dengan Playwright.

Menguji alur pengguna dari splash sampai hasil, termasuk keadaan khusus
(luar sebaran, input buruk), sambil menyimpan tangkapan layar ke
docs/tangkapan-layar untuk laporan dan presentasi.

Jalankan (server harus hidup di port 8000):
    python tests/perjalanan_ui.py
"""

import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KELUAR = os.path.join(ROOT, "docs", "tangkapan-layar")
os.makedirs(KELUAR, exist_ok=True)

LANGKAH = []


def catat(nama, status, catatan=""):
    LANGKAH.append((nama, status, catatan))
    print(f"[{status}] {nama} {catatan}")


def cek_luapan(hal, layar):
    """Pastikan tidak ada luapan horizontal pada lebar 390px (R-03)."""
    luapan = hal.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert luapan <= 0, f"luapan horizontal {luapan}px pada layar {layar}"


def jalankan():
    galat_konsol = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        konteks = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            locale="id-ID",
        )
        hal = konteks.new_page()
        hal.on("console", lambda m: galat_konsol.append(m.text) if m.type == "error" else None)
        hal.on("pageerror", lambda e: galat_konsol.append(str(e)))

        url = "http://127.0.0.1:8000"
        hal.goto(url)
        hal.wait_for_selector("#v-splash:not([hidden])")
        hal.screenshot(path=os.path.join(KELUAR, "01-splash.png"))
        catat("splash tampil", "OK")

        # consent belum dicentang -> galat tampil
        hal.click("#tombol-masuk")
        assert hal.is_visible("#galat-setuju"), "galat consent tidak tampil"
        catat("galat consent tanpa centang", "OK")

        hal.check("#cek-setuju")
        hal.click("#tombol-masuk")
        hal.wait_for_selector("#v-beranda:not([hidden])")
        cek_luapan(hal, "beranda")
        hal.screenshot(path=os.path.join(KELUAR, "02-beranda-kosong.png"))
        catat("beranda keadaan kosong", "OK")

        # lahan kosong
        hal.click(".nav-item[data-buka='lahan']")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        assert "Belum ada lahan" in hal.inner_text("#daftar-lahan")
        catat("lahan keadaan kosong", "OK")

        # tambah lahan via peta
        hal.click(".baris-judul .tombol.kecil")
        hal.wait_for_selector("#v-tambah-lahan:not([hidden])")
        catat("layar pilih sumber lahan", "OK")
        hal.screenshot(path=os.path.join(KELUAR, "03-tambah-lahan.png"))

        hal.click(".pilihan-sumber[data-buka='peta']")
        hal.wait_for_selector("#peta-svg:not([hidden])", timeout=15000)
        cek_luapan(hal, "peta")
        hal.screenshot(path=os.path.join(KELUAR, "04-peta-zona.png"))
        catat("peta zona termuat", "OK")

        hal.click(".peta-zona-grup[data-zona='Z01']")
        hal.wait_for_selector("#zona-pakai")
        hal.fill("#zona-nama", "Sawah Cibinong")
        hal.screenshot(path=os.path.join(KELUAR, "05-peta-zona-detail.png"))
        hal.click("#zona-pakai")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        assert "Sawah Cibinong" in hal.inner_text("#daftar-lahan")
        catat("lahan dari peta terdaftar", "OK")

        # tambah lahan kedua via uji tanah: pH 5.4, P sangat rendah (masuk sebaran)
        hal.click(".baris-judul .tombol.kecil")
        hal.wait_for_selector("#v-tambah-lahan:not([hidden])")
        hal.click(".pilihan-sumber[data-buka='uji-tanah']")
        hal.wait_for_selector("#form-uji-tanah")
        # uji dulu validasi input buruk
        hal.fill("#ut-nama", "Sawah Belakang")
        hal.fill("#ut-ph", "9.4")
        hal.fill("#ut-n", "0.35")
        hal.fill("#ut-p", "8")
        hal.fill("#ut-k", "0.18")
        hal.fill("#ut-luas", "0.5")
        hal.click("#form-uji-tanah button[type='submit']")
        assert hal.is_visible("#galat-uji-tanah"), "galat pH 9,4 tidak tampil"
        hal.screenshot(path=os.path.join(KELUAR, "06-uji-tanah-galat-input.png"))
        catat("form uji tanah menolak pH 9,4", "OK")

        hal.fill("#ut-ph", "5.4")
        hal.fill("#ut-p", "7")
        hal.click("#form-uji-tanah button[type='submit']")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        assert "Sawah Belakang" in hal.inner_text("#daftar-lahan")
        hal.screenshot(path=os.path.join(KELUAR, "07-lahan-dua-petak.png"))
        catat("lahan dari uji tanah terdaftar", "OK")

        # rekomendasi: pilih lahan kedua (uji tanah), padi
        hal.click(".nav-item[data-buka='rekomendasi']")
        hal.wait_for_selector("#v-rekomendasi:not([hidden])")
        cek_luapan(hal, "rekomendasi")
        hal.click("[data-pilih-lahan]:nth-child(2)")
        hal.screenshot(path=os.path.join(KELUAR, "08-form-rekomendasi.png"))
        catat("form rekomendasi terisi", "OK")

        hal.click("#tombol-hitung")
        hal.wait_for_selector("#v-hasil:not([hidden])", timeout=30000)
        hal.wait_for_selector(".kartu-dosis")
        cek_luapan(hal, "hasil")
        hal.screenshot(path=os.path.join(KELUAR, "09-hasil-rekomendasi.png"), full_page=True)
        catat("hasil rekomendasi tampil (alur 3 ketukan dari beranda)", "OK")

        # pindah paket optimal -> biaya berubah
        biaya_standar = hal.inner_text("#angka-biaya")
        hal.click("[data-paket='optimal']")
        biaya_optimal = hal.inner_text("#angka-biaya")
        assert biaya_standar != biaya_optimal, "paket tidak mengubah biaya"
        hal.screenshot(path=os.path.join(KELUAR, "10-hasil-paket-optimal.png"))
        catat("paket optimal mengubah kebutuhan dan biaya", "OK")

        # kirim ke penyuluh
        hal.click("#kirim-penyuluh")
        hal.wait_for_selector("#toast:not([hidden])")
        catat("kirim ke penyuluh", "OK")

        # riwayat
        hal.click(".tombol.garis.lebar[data-buka='riwayat']")
        hal.wait_for_selector("#v-riwayat:not([hidden])")
        assert "Sawah Belakang" in hal.inner_text("#daftar-riwayat")
        hal.screenshot(path=os.path.join(KELUAR, "11-riwayat.png"))
        catat("riwayat tersimpan", "OK")

        # penyuluhan: setujui verifikasi (item menghilang dari daftar menunggu)
        hal.click(".nav-item[data-buka='penyuluhan']")
        hal.wait_for_selector("#v-penyuluhan:not([hidden])")
        hal.wait_for_selector("[data-setujui]")
        hal.click("[data-setujui]")
        hal.wait_for_function("document.querySelector('#daftar-verifikasi').textContent.includes('Tidak ada permintaan verifikasi')", timeout=8000)
        hal.screenshot(path=os.path.join(KELUAR, "12-penyuluhan.png"))
        catat("verifikasi penyuluh disetujui (keluar dari daftar menunggu)", "OK")

        # profil: metrik model
        hal.click(".nav-item[data-buka='profil']")
        hal.wait_for_selector("#v-profil:not([hidden])")
        hal.wait_for_function("document.querySelector('#profil-model').textContent.includes('Random Forest')", timeout=15000)
        hal.screenshot(path=os.path.join(KELUAR, "13-profil.png"))
        catat("profil menampilkan metrik model nyata", "OK")

        # kasus luar sebaran: uji tanah P 150 ppm
        hal.click(".nav-item[data-buka='lahan']")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        hal.click(".baris-judul .tombol.kecil")
        hal.wait_for_selector("#v-tambah-lahan:not([hidden])")
        hal.click(".pilihan-sumber[data-buka='uji-tanah']")
        hal.wait_for_selector("#form-uji-tanah")
        hal.fill("#ut-nama", "Lahan Ekstrem")
        hal.fill("#ut-ph", "5.9")
        hal.fill("#ut-n", "0.40")
        hal.fill("#ut-p", "150")
        hal.fill("#ut-k", "0.20")
        hal.fill("#ut-luas", "0.4")
        hal.click("#form-uji-tanah button[type='submit']")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        hal.click(".nav-item[data-buka='rekomendasi']")
        hal.wait_for_selector("#v-rekomendasi:not([hidden])")
        # pilih chip Lahan Ekstrem (chip terakhir)
        hal.click("[data-pilih-lahan] >> nth=-1")
        hal.click("#tombol-hitung")
        hal.wait_for_selector("#v-hasil:not([hidden])", timeout=30000)
        teks = hal.inner_text("#isi-hasil")
        assert "ANGKA TIDAK DITAMPILKAN" in teks.upper(), "keadaan luar sebaran tidak tampil"
        hal.screenshot(path=os.path.join(KELUAR, "14-hasil-luar-sebaran.png"), full_page=True)
        catat("keadaan luar sebaran menyembunyikan angka", "OK")

        # kasus keyakinan tinggi: jagung pada lahan normal dari peta (chip pertama)
        hal.click(".tombol-kembali[data-buka='rekomendasi']")
        hal.wait_for_selector("#v-rekomendasi:not([hidden])")
        hal.click("[data-pilih-lahan] >> nth=0")
        hal.click(".segmen[data-komoditas='Jagung']")
        hal.click("#tombol-hitung")
        hal.wait_for_selector("#v-hasil:not([hidden])", timeout=30000)
        hal.wait_for_selector(".kartu-dosis")
        badge = hal.inner_text("#badge-keyakinan")
        catat("hasil jagung", "OK", badge)
        hal.screenshot(path=os.path.join(KELUAR, "15-hasil-jagung.png"), full_page=True)

        browser.close()

    print()
    print("=== RINGKASAN PERJALANAN ===")
    for nama, status, catatan in LANGKAH:
        print(f"{status} {nama} {catatan}")
    if galat_konsol:
        print()
        print("GALAT KONSOL:", galat_konsol)
        return 1
    print("Tanpa galat konsol.")
    return 0


if __name__ == "__main__":
    sys.exit(jalankan())
