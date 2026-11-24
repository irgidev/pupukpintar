# -*- coding: utf-8 -*-
"""
Pembangkit desain high-fidelity tiga layar PupukPintar dalam format SVG
(390x844, siap diimpor ke Figma: File > Place image, atau seret berkas SVG
langsung ke kanvas Figma).

Desain mengikuti apa yang benar-benar dibangun pada aplikasi (Bab 6 laporan):
palet hijau padi, font Plus Jakarta Sans, kartu dosis, badge keyakinan,
paket sesuai modal, peringatan dini, dan disclaimer.

Jalankan dari folder ini:
    python buat_desain_svg.py
"""

TIPO = "'Plus Jakarta Sans', 'Segoe UI', sans-serif"

# token warna (sama dengan app/frontend/styles.css)
HIJAU_900 = "#143D2B"
HIJAU_700 = "#1E5B3F"
HIJAU_100 = "#E4EEE6"
KUNING = "#F2C14E"
KUNING_GELAP = "#7A5410"
KUNING_MUDA = "#F9EED6"
MERAH = "#A3352C"
MERAH_MUDA = "#F6E0DD"
BG = "#F3F4EE"
KARTU = "#FFFFFF"
GARIS = "#DCE0D6"
TINTA = "#1D241F"
ABU = "#55635A"


def teks(x, y, isi, ukuran=14, bobot=400, warna=TINTA, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family={TIPO} font-size="{ukuran}" '
            f'font-weight="{bobot}" fill="{warna}" text-anchor="{anchor}">{isi}</text>')


def kartu(x, y, w, h, radius=10, fill=KARTU, stroke=GARIS, sw=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def tombol(x, y, w, h, label, utama=True, fs=15):
    if utama:
        isi = kartu(x, y, w, h, 8, HIJAU_700, HIJAU_700) + teks(x + w / 2, y + h / 2 + 5, label, fs, 700, "#FFFFFF", "middle")
    else:
        isi = kartu(x, y, w, h, 8, KARTU, HIJAU_700, 1.5) + teks(x + w / 2, y + h / 2 + 5, label, fs, 700, HIJAU_700, "middle")
    return isi


def chip(x, y, label, fc, tc):
    w = 12 + len(label) * 6.4
    return (kartu(x, y, w, 22, 11, fc, fc) + teks(x + w / 2, y + 15, label, 11.5, 700, tc, "middle"), w)


def kepala(judul):
    return (
        kartu(0, 0, 390, 56, 0, BG, BG)
        + f'<circle cx="34" cy="28" r="11" fill="{HIJAU_700}"/>'
        + f'<path d="M34 21c-3.2 2.4-5.2 4.8-5.2 7.6a5.2 5.2 0 0 0 10.4 0c0-2.8-2-5.2-5.2-7.6Z" fill="none" stroke="#fff" stroke-width="1.6"/>'
        + f'<path d="M34 36.5v-4" stroke="{KUNING}" stroke-width="1.6" stroke-linecap="round"/>'
        + teks(52, 33, "PupukPintar", 15, 800, HIJAU_700)
        + kartu(296, 14, 62, 26, 13, HIJAU_100, HIJAU_100)
        + teks(327, 31, "Online", 11, 600, HIJAU_700, "middle")
        + teks(24, 86, judul, 22, 800, HIJAU_900)
    )


def nav_bawah(aktif):
    nama = ["Beranda", "Lahan", "Rekomendasi", "Penyuluhan", "Profil"]
    hasil = kartu(0, 780, 390, 64, 0, "#FFFFFF", GARIS)
    for i, n in enumerate(nama):
        cx = 39 + i * 78
        warna = HIJAU_700 if n == aktif else ABU
        bobot = 700 if n == aktif else 600
        hasil += teks(cx, 832, n, 10.5, bobot, warna, "middle")
        hasil += f'<circle cx="{cx}" cy="800" r="7" fill="{warna}" opacity="0.85"/>'
    return hasil


def layar_splash():
    isi = [f'<rect width="390" height="844" fill="{BG}"/>']
    isi.append(f'<circle cx="195" cy="220" r="48" fill="{HIJAU_700}"/>')
    isi.append('<path d="M195 192c-9.6 7.2-15.7 14.4-15.7 22.8a15.7 15.7 0 0 0 31.4 0c0-8.4-6.1-15.6-15.7-22.8Z" fill="none" stroke="#fff" stroke-width="2.6"/>')
    isi.append(f'<path d="M195 238v-10" stroke="{KUNING}" stroke-width="2.6" stroke-linecap="round"/>')
    isi.append(teks(195, 320, "PupukPintar", 30, 800, HIJAU_900, "middle"))
    isi.append(teks(195, 352, "Rekomendasi dosis pupuk N-P-K presisi", 14.5, 400, ABU, "middle"))
    isi.append(teks(195, 374, "untuk lahan Anda, bukan lahan tetangga.", 14.5, 400, ABU, "middle"))

    isi.append(kartu(20, 410, 350, 138))
    isi.append(teks(36, 440, "Persetujuan Data", 16, 700, HIJAU_900))
    isi.append(teks(36, 464, "Data lahan Anda dipakai untuk rekomendasi pribadi", 13, 400, ABU))
    isi.append(teks(36, 483, "dan perbaikan model. Identitas disamarkan dan", 13, 400, ABU))
    isi.append(teks(36, 502, "bisa dihapus kapan saja dari halaman Profil.", 13, 400, ABU))
    isi.append(f'<rect x="36" y="516" width="20" height="20" rx="4" fill="#fff" stroke="{ABU}" stroke-width="1.6"/>')
    isi.append(teks(64, 531, "Saya setuju data saya dipakai", 13.5, 600, TINTA))

    isi.append(tombol(20, 570, 350, 50, "Masuk"))
    isi.append(tombol(20, 630, 350, 50, "Daftar", utama=False))
    isi.append(teks(195, 712, "Butuh bantuan? Hubungi penyuluh di poktan Anda.", 12.5, 400, ABU, "middle"))
    return "\n".join(isi)


def layar_form():
    isi = [f'<rect width="390" height="844" fill="{BG}"/>']
    isi.append(kepala("Rekomendasi Dosis"))
    isi.append(teks(24, 112, "Pilih lahan dan kebutuhan tanam Anda.", 14, 400, ABU))

    # kartu petak lahan
    isi.append(kartu(20, 136, 350, 148))
    isi.append(teks(36, 164, "PETAK LAHAN", 11, 700, ABU))
    isi.append(chip(36, 176, "Sawah Cibinong", "#fff", ABU)[0])
    isi.append(chip(36, 204, "Sawah Belakang", HIJAU_700, "#FFFFFF")[0])
    isi.append(teks(36, 246, "pH 5,4 · N 0,35 · P 7 ppm · K 0,18 · Lempung · luas 0,5 ha", 12.5, 400, ABU))
    isi.append(teks(36, 264, "(dari uji tanah)", 12.5, 400, ABU))

    # kartu komoditas
    isi.append(kartu(20, 300, 350, 240))
    isi.append(teks(36, 328, "KOMODITAS", 11, 700, ABU))
    isi.append(kartu(36, 340, 160, 44, 8, "#EDEFE7", "#EDEFE7"))
    isi.append(kartu(42, 346, 148, 32, 7, "#fff", GARIS))
    isi.append(teks(116, 368, "Padi", 15, 700, TINTA, "middle"))
    isi.append(teks(287, 368, "Jagung", 15, 700, ABU, "middle"))
    isi.append(teks(36, 412, "Target hasil (ton/ha)", 13, 700, HIJAU_900))
    isi.append(kartu(36, 420, 160, 42, 8))
    isi.append(teks(48, 447, "6", 15, 500, TINTA))
    isi.append(teks(206, 412, "Luas petak (ha)", 13, 700, HIJAU_900))
    isi.append(kartu(206, 420, 148, 42, 8))
    isi.append(teks(218, 447, "0,5", 15, 500, TINTA))
    isi.append(teks(36, 490, "Musim tanam", 13, 700, HIJAU_900))
    isi.append(kartu(36, 498, 318, 42, 8))
    isi.append(teks(48, 525, "Hujan (Oktober sampai Maret)", 14, 500, TINTA))
    isi.append(f'<path d="M340 514l6 6 6-6" fill="none" stroke="{ABU}" stroke-width="2"/>')

    isi.append(tombol(20, 564, 350, 52, "Hitung Rekomendasi"))
    isi.append(teks(195, 640, "Hasil tampil dalam hitungan detik. Keluaran dikunci pada", 12.5, 400, ABU, "middle"))
    isi.append(teks(195, 658, "rentang aman rekomendasi resmi.", 12.5, 400, ABU, "middle"))
    isi.append(nav_bawah("Rekomendasi"))
    return "\n".join(isi)


def layar_hasil():
    isi = [f'<rect width="390" height="844" fill="{BG}"/>']
    isi.append(kartu(0, 0, 390, 56, 0, BG, BG))
    isi.append(kartu(20, 12, 40, 36, 8, "#fff", GARIS))
    isi.append(f'<path d="M38 24l7 6-7 6" fill="none" stroke="{HIJAU_700}" stroke-width="2.4" stroke-linecap="round"/>')
    isi.append(teks(74, 36, "Hasil Rekomendasi", 19, 800, HIJAU_900))
    isi.append(kartu(148, 66, 222, 30, 15, KUNING_MUDA, KUNING_MUDA))
    isi.append(teks(259, 86, "Keyakinan 84% (Cukup yakin)", 13, 700, KUNING_GELAP, "middle"))

    # tiga kartu dosis
    dosis = [("N (UREA)", "207", "150-250"), ("P (SP-36)", "83", "50-100"), ("K (KCl)", "51", "25-75")]
    for i, (u, a, r) in enumerate(dosis):
        x = 20 + i * 120
        isi.append(kartu(x, 112, 110, 106))
        isi.append(teks(x + 55, 136, u, 10.5, 800, ABU, "middle"))
        isi.append(teks(x + 55, 176, a, 28, 800, HIJAU_900, "middle"))
        isi.append(teks(x + 55, 194, "kg/ha", 11, 400, ABU, "middle"))
        isi.append(teks(x + 55, 210, "rentang " + r, 9.5, 400, ABU, "middle"))

    # kebutuhan per petak
    isi.append(kartu(20, 234, 350, 148))
    isi.append(teks(36, 262, "KEBUTUHAN PUPUK PER PETAK (0,5 ha)", 11, 700, ABU))
    baris = [("Urea", "169 kg"), ("SP-36", "138 kg"), ("KCl", "43 kg")]
    for i, (k, v) in enumerate(baris):
        y = 288 + i * 27
        isi.append(teks(36, y, k, 13.5, 500, TINTA))
        isi.append(teks(354, y, v, 13.5, 700, TINTA, "end"))
        if i < 2:
            isi.append(f'<line x1="36" y1="{y + 8}" x2="354" y2="{y + 8}" stroke="{GARIS}" stroke-dasharray="3 3"/>')
    isi.append(teks(36, 370, "Estimasi biaya", 13, 400, ABU))
    isi.append(teks(354, 371, "Rp 1.063.300", 17, 800, HIJAU_900, "end"))

    # paket
    isi.append(kartu(20, 398, 350, 118))
    isi.append(teks(36, 426, "PAKET SESUAI MODAL", 11, 700, ABU))
    isi.append(kartu(36, 438, 318, 44, 8, "#EDEFE7", "#EDEFE7"))
    segmen = [("Hemat", 42, False), ("Standar", 178, True), ("Optimal", 298, False)]
    for label, x, aktif in segmen:
        w = 122 if label != "Standar" else 122
        if aktif:
            isi.append(kartu(x, 444, w, 32, 7, "#fff", GARIS))
        isi.append(teks(x + w / 2, 465, label, 14, 700 if aktif else 600, TINTA if aktif else ABU, "middle"))
    isi.append(teks(36, 502, "Standar: dosis penuh sesuai rekomendasi model.", 12.5, 400, ABU))

    # penjelasan
    isi.append(kartu(20, 532, 350, 132))
    isi.append(teks(36, 560, "PENJELASAN SEDERHANA", 11, 700, ABU))
    isi.append(teks(36, 584, "Dosis N sedang karena stok nitrogen lahan Anda", 13, 400, TINTA))
    isi.append(teks(36, 603, "sedang. P dinaikkan karena tanah masam sehingga", 13, 400, TINTA))
    isi.append(teks(36, 622, "fosfor mudah terikat. K dinaikkan karena stok kalium", 13, 400, TINTA))
    isi.append(teks(36, 641, "lahan rendah. Target hasil 6 ton/ha ikut menaikkan", 13, 400, TINTA))
    isi.append(teks(36, 660, "kebutuhan hara.", 13, 400, TINTA))

    # peringatan
    isi.append(kartu(20, 680, 350, 58, 8, KUNING_MUDA, KUNING_MUDA))
    isi.append(f'<path d="M38 702l7-12 7 12Z" fill="none" stroke="{KUNING_GELAP}" stroke-width="1.8"/>')
    isi.append(teks(60, 700, "Tanah masam (pH 5,4). Pertimbangkan pengapuran", 12.5, 600, KUNING_GELAP))
    isi.append(teks(60, 718, "karena fosfor mudah terikat.", 12.5, 600, KUNING_GELAP))

    isi.append(kartu(20, 750, 350, 56, 8, HIJAU_100, HIJAU_100))
    isi.append(f'<circle cx="38" cy="770" r="8" fill="none" stroke="{HIJAU_900}" stroke-width="1.6"/>')
    isi.append(teks(38, 774, "i", 10, 800, HIJAU_900, "middle"))
    isi.append(teks(56, 770, "Rekomendasi awal dari model, bukan pengganti uji tanah", 11.5, 400, HIJAU_900))
    isi.append(teks(56, 786, "laboratorium. Verifikasi penyuluh sebelum pembelian.", 11.5, 400, HIJAU_900))
    return "\n".join(isi)


def bungkus(nama, isi):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844" '
           f'viewBox="0 0 390 844">\n{isi}\n</svg>')
    with open(nama, "w", encoding="utf-8") as f:
        f.write(svg)
    print("tersimpan:", nama)


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    bungkus("layar-1-splash.svg", layar_splash())
    bungkus("layar-2-form-rekomendasi.svg", layar_form())
    bungkus("layar-3-hasil.svg", layar_hasil())
