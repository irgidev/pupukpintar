# -*- coding: utf-8 -*-
"""
Perekaman video demo PupukPintar dengan gerakan ala pengguna manusia.

Merekam perjalanan lengkap aplikasi (dari pembuka sampai profil) dengan
kecepatan wajar, kursor bergerak mulus, dan jeda berpikir antar langkah.
Menghasilkan berkas .webm beserta timeline.json (waktu mulai, durasi, teks
penjelasan, dan posisi target panah untuk setiap langkah).

Jalankan (server harus hidup di port 8000):
    python tests/video_demo.py
"""

import json
import os
import random
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KELUAR = os.path.join(ROOT, "video_demo")
os.makedirs(KELUAR, exist_ok=True)

LEBAR, TINGGI = 390, 844

CURSOR_JS = """
window.__gerak = (x, y) => {
    let el = document.getElementById('vcursor');
    if (!el) {
        el = document.createElement('div');
        el.id = 'vcursor';
        el.style.cssText = 'position:fixed;width:26px;height:26px;border-radius:50%;'
            + 'background:rgba(15,40,70,0.82);border:3px solid #F2C14E;'
            + 'z-index:99999;pointer-events:none;left:60%;top:35%;'
            + 'transition:left 0.22s ease-out, top 0.22s ease-out;';
        (document.body || document.documentElement).appendChild(el);
    }
    el.style.left = x + 'px';
    el.style.top = y + 'px';
};
try { window.__gerak(300, 700); } catch (e) {}
"""


def main():
    timeline = []
    galat_konsol = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        konteks = browser.new_context(
            viewport={"width": LEBAR, "height": TINGGI},
            record_video_dir=KELUAR,
            record_video_size={"width": LEBAR * 2, "height": TINGGI * 2},
            locale="id-ID",
        )
        hal = konteks.new_page()
        hal.on("pageerror", lambda e: galat_konsol.append(str(e)[:120]))
        hal.add_init_script(CURSOR_JS)
        hal.wait_for_timeout(250)
        t0 = time.time()

        def jeda(d=None):
            hal.wait_for_timeout(d if d is not None else random.uniform(650, 1100))

        def pusat(pos):
            if "width" in pos:
                return pos["x"] + pos["width"] / 2, pos["y"] + pos["height"] / 2
            return pos["x"], pos["y"]

        def gerak_ke(pos):
            cx, cy = pusat(pos)
            hal.evaluate("p => window.__gerak(p[0], p[1])", [cx, cy])
            hal.mouse.move(cx, cy, steps=16)
            jeda(random.uniform(220, 380))

        def klik(pos):
            gerak_ke(pos)
            hal.mouse.down()
            hal.wait_for_timeout(90)
            hal.mouse.up()
            jeda(random.uniform(650, 950))

        def klik_pemilih(pemilih):
            lok = hal.locator(pemilih).first
            lok.wait_for(state="visible", timeout=15000)
            lok.scroll_into_view_if_needed(timeout=5000)
            jeda(250)
            klik(lok.bounding_box())
            return lok

        def isi(pemilih, teks):
            lok = hal.locator(pemilih).first
            lok.wait_for(state="visible", timeout=15000)
            lok.scroll_into_view_if_needed(timeout=5000)
            jeda(250)
            klik(lok.bounding_box())
            lok.type(teks, delay=random.uniform(55, 95))
            jeda(250)

        def catat(mulai, durasi, teks, panah=None):
            timeline.append({"mulai": round(mulai - t0, 2), "durasi": round(durasi, 2),
                             "teks": teks, "panah": panah})

        # ---------- 0. pembuka: splash dan persetujuan ----------
        hal.goto("http://127.0.0.1:8000")
        hal.wait_for_selector("#v-splash:not([hidden])")
        jeda(1500)
        m = time.time()
        catat(m, 4.0, "Halaman pembuka PupukPintar: aplikasi rekomendasi dosis pupuk N-P-K per lahan")
        klik_pemilih("#cek-setuju")
        catat(time.time(), 2.2, "Pengguna menyetujui pengelolaan data sebelum memakai aplikasi", [60, 1058])
        klik_pemilih("#tombol-masuk")
        hal.wait_for_selector("#v-beranda:not([hidden])")
        jeda(900)

        # ---------- 1. beranda kosong ----------
        m = time.time()
        catat(m, 3.4, "Beranda: ringkasan lahan aktif dan pintasan cepat ke fitur utama")
        hal.screenshot(path=os.path.join(KELUAR, "b_01_beranda.png"))
        jeda(1200)

        # ---------- 2. peta unit lahan ----------
        klik_pemilih(".nav-item[data-buka='lahan']")
        jeda(600)
        klik_pemilih(".baris-judul .tombol.kecil")
        hal.wait_for_selector("#v-tambah-lahan:not([hidden])")
        jeda(500)
        klik_pemilih(".pilihan-sumber[data-buka='peta']")
        hal.wait_for_selector("#peta-svg .peta-area", timeout=20000)
        jeda(900)
        m = time.time()
        catat(m, 5.0, "Peta vektor 191 unit lahan SAFRONS wilayah Bogor, bekerja tanpa internet",
              [190, 1520])
        jeda(700)

        titik = hal.evaluate("window.__ppPeta.latlngKeKlien(-6.6, 106.8)")
        klik(titik)
        hal.wait_for_selector("#area-pakai", timeout=8000)
        catat(time.time(), 4.5, "Unit Bogor dipilih: peta membesarkan unit dengan label nama",
              [390, 1280])
        jeda(500)
        isi("#area-nama", "Sawah Bogor Uji")
        isi("#area-luas", "0.75")
        klik_pemilih("#area-pakai")
        hal.wait_for_selector("#v-lahan:not([hidden])")
        jeda(800)
        m = time.time()
        catat(m, 3.4, "Lahan tersimpan: unit peta, pH, dan status hara ikut tercatat")
        hal.screenshot(path=os.path.join(KELUAR, "b_02_lahan.png"))
        jeda(900)

        # ---------- 3. formulir rekomendasi ----------
        klik_pemilih(".nav-item[data-buka='rekomendasi']")
        hal.wait_for_selector("#v-rekomendasi:not([hidden])")
        jeda(800)
        m = time.time()
        catat(m, 4.6, "Formulir rekomendasi: pilih petak lahan, komoditas, dan target hasil",
              [190, 1620])
        jeda(600)
        klik_pemilih("#tombol-hitung")
        hal.wait_for_selector("#v-hasil:not([hidden])", timeout=30000)
        jeda(700)
        m = time.time()
        catat(m, 5.0, "Hasil AI: dosis N-P-K per lahan dengan tingkat keyakinan model",
              [390, 800])
        hal.screenshot(path=os.path.join(KELUAR, "b_03_hasil.png"))
        jeda(600)

        klik_pemilih("[data-paket='optimal']")
        jeda(700)
        m = time.time()
        catat(m, 3.4, "Paket sesuai modal: kebutuhan pupuk per petak dan estimasi biaya berubah")
        hal.screenshot(path=os.path.join(KELUAR, "b_04_paket.png"))
        jeda(500)

        klik_pemilih("#kirim-penyuluh")
        hal.wait_for_timeout(2900)  # biarkan toast hilang sebelum menekan tombol berikutnya
        catat(time.time(), 3.2, "Hasil dikirim ke penyuluh untuk verifikasi sebelum dipakai")

        klik_pemilih(".tombol.garis.lebar[data-buka='riwayat']")
        hal.wait_for_selector("#v-riwayat:not([hidden])")
        jeda(700)
        m = time.time()
        catat(m, 3.2, "Riwayat rekomendasi tersimpan per petak dan per musim")
        jeda(700)

        klik_pemilih(".nav-item[data-buka='penyuluhan']")
        hal.wait_for_selector("#v-penyuluhan:not([hidden])")
        jeda(700)
        m = time.time()
        catat(m, 3.4, "Papan penyuluhan: tips pemupukan dan verifikasi oleh penyuluh")
        hal.screenshot(path=os.path.join(KELUAR, "b_05_penyuluhan.png"))
        jeda(600)

        klik_pemilih(".nav-item[data-buka='profil']")
        hal.wait_for_selector("#v-profil:not([hidden])")
        hal.wait_for_function("document.querySelector('#profil-model').textContent.includes('Random Forest')", timeout=15000)
        jeda(600)
        m = time.time()
        catat(m, 4.2, "Profil: metrik model transparan (agreement 95 persen pada data uji)")
        hal.screenshot(path=os.path.join(KELUAR, "b_06_profil.png"))
        jeda(600)

        video = hal.video.path()
        konteks.close()

    with open(os.path.join(KELUAR, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=1)
    print("video:", video)
    print("langkah:", len(timeline))
    if galat_konsol:
        print("GALAT KONSOL:", galat_konsol[:3])


if __name__ == "__main__":
    main()
