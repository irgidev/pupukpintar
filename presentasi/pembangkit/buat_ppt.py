# -*- coding: utf-8 -*-
"""
Pembangkit PPT Demo Day PupukPintar (Kelompok 14).

Basis desain: Template PPT IPB.pptx (tema IPB University, palet biru IPB dan
kuning, font Inter Tight, band pola bawaan template). Struktur isi mengikuti
Template_Presentasi_Demo_Day.pptx, slide demi slide, dengan data nyata proyek.

Jalankan dari folder presentasi/pembangkit:
    python buat_ppt.py
"""

import copy
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

SINI = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.normpath(os.path.join(SINI, "..", "..", "..", "proyek_akhir", "Template PPT IPB.pptx"))
LAYAR = os.path.normpath(os.path.join(SINI, "..", "..", "docs", "tangkapan-layar"))
KELUAR = os.path.normpath(os.path.join(SINI, "..", "Presentasi_Demo_Day_PupukPintar_Kelompok14.pptx"))

# palet tema IPB dari theme1.xml
NAVY = RGBColor(0x0E, 0x28, 0x41)
BIRU = RGBColor(0x26, 0x3C, 0x92)
BIRU2 = RGBColor(0x31, 0x4C, 0xBB)
BIRU3 = RGBColor(0x4D, 0x68, 0xD1)
KUNING = RGBColor(0xFE, 0xD8, 0x0B)
KUNING_MUDA = RGBColor(0xFE, 0xE0, 0x3E)
PUTIH = RGBColor(0xFF, 0xFF, 0xFF)
ABU_TERANG = RGBColor(0xE8, 0xE8, 0xE8)
TINTA = RGBColor(0x1D, 0x24, 0x1F)
ABU = RGBColor(0x5C, 0x6B, 0x63)
HIJAU_MUDA_KARTU = RGBColor(0xEA, 0xF1, 0xEC)
PUTIH_SUSU = RGBColor(0xF6, 0xF7, 0xF3)

F_JUDUL = "Inter Tight SemiBold"
F_TEKS = "Inter Tight"

prs = Presentation(TEMPLATE)
MASTER = prs.slide_masters[0]
LAYOUT_CLOSING = MASTER.slide_layouts[16]
LAYOUT_KONTEN = MASTER.slide_layouts[2]


# ----------------------------------------------------------------------
# pembersihan slide contoh
# ----------------------------------------------------------------------
def hapus_semua_slide():
    xml_slides = prs.slides._sldIdLst
    for sld_id in list(xml_slides):
        rId = sld_id.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        prs.part.drop_rel(rId)
        xml_slides.remove(sld_id)


def slide_baru(layout):
    s = prs.slides.add_slide(layout)
    # hapus placeholder contoh agar tidak menampilkan prompt
    for sh in list(s.shapes):
        if sh.is_placeholder:
            sh._element.getparent().remove(sh._element)
    return s


# ----------------------------------------------------------------------
# pembantu gambar
# ----------------------------------------------------------------------

def kotak_teks(slide, x, y, w, h, isi, ukuran=12, tebal=False, warna=TINTA, rata=PP_ALIGN.LEFT,
               font=None, baris=1.15, jangkar=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = jangkar
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    baris_list = isi.split("\n")
    for i, b in enumerate(baris_list):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = rata
        par.line_spacing = baris
        run = par.add_run()
        run.text = b
        run.font.size = Pt(ukuran)
        run.font.bold = tebal
        run.font.color.rgb = warna
        run.font.name = font or (F_JUDUL if tebal else F_TEKS)
    return tb


def kartu(slide, x, y, w, h, isi=None, warna_isi=PUTIH, garis=None, radius=0.08, judul=None,
          judul_warna=None, isi_ukuran=11, judul_ukuran=12, isi_warna=TINTA, isi_rata=PP_ALIGN.LEFT,
          judul_warna_def=BIRU):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = radius
    sh.fill.solid()
    sh.fill.fore_color.rgb = warna_isi
    if garis is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = garis
        sh.line.width = Pt(1)
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.14)
    tf.margin_right = Inches(0.14)
    tf.margin_top = Inches(0.09)
    tf.margin_bottom = Inches(0.07)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    if judul:
        par = tf.paragraphs[0]
        par.line_spacing = 1.05
        run = par.add_run()
        run.text = judul
        run.font.size = Pt(judul_ukuran)
        run.font.bold = True
        run.font.color.rgb = judul_warna if judul_warna else judul_warna_def
        run.font.name = F_JUDUL
        if isi:
            tf.paragraphs[0].space_after = Pt(4)
    if isi:
        for i, b in enumerate(isi.split("\n")):
            par = tf.paragraphs[0] if (i == 0 and not judul) else tf.add_paragraph()
            par.alignment = isi_rata
            par.line_spacing = 1.12
            run = par.add_run()
            run.text = b
            run.font.size = Pt(isi_ukuran)
            run.font.color.rgb = isi_warna
            run.font.name = F_TEKS
    return sh


def pil(slide, x, y, w, h, teks, latar=KUNING, warna_teks=NAVY, ukuran=10.5):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.5
    sh.fill.solid()
    sh.fill.fore_color.rgb = latar
    sh.line.fill.background()
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = 0
    tf.margin_bottom = 0
    par = tf.paragraphs[0]
    par.alignment = PP_ALIGN.CENTER
    run = par.add_run()
    run.text = teks
    run.font.size = Pt(ukuran)
    run.font.bold = True
    run.font.color.rgb = warna_teks
    run.font.name = F_JUDUL
    return sh


def garis_kuning(slide, x, y, w, tebal=0.045):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(tebal))
    sh.fill.solid()
    sh.fill.fore_color.rgb = KUNING
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def kepala_konten(slide, kicker, judul, kriteria=None, nomor=None):
    pil(slide, 0.55, 0.92, 3.4, 0.34, kicker, latar=BIRU, warna_teks=PUTIH, ukuran=10.5)
    if kriteria:
        pil(slide, 9.05, 0.92, 3.73, 0.34, kriteria, latar=KUNING, warna_teks=NAVY, ukuran=10.5)
    kotak_teks(slide, 0.55, 1.38, 11.0, 0.62, judul, ukuran=27, tebal=True, warna=NAVY, font=F_JUDUL)
    if nomor:
        kotak_teks(slide, 12.4, 6.82, 0.5, 0.3, str(nomor), ukuran=10, warna=ABU, rata=PP_ALIGN.RIGHT)


def catatan(slide, teks):
    slide.notes_slide.notes_text_frame.text = teks


def tambah_tangkapan(slide, nama_berkas, x, y, tinggi):
    from PIL import Image
    jalur = os.path.join(LAYAR, nama_berkas)
    with Image.open(jalur) as im:
        rasio = im.height / im.width
    w = tinggi / rasio
    slide.shapes.add_picture(jalur, Inches(x), Inches(y), height=Inches(tinggi))
    return w


# ======================================================================
# SLIDE 1 SAMPUL
# ======================================================================
def slide1():
    s = slide_baru(LAYOUT_CLOSING)
    kotak_teks(s, 0.9, 0.62, 11.5, 0.35,
               "KEB1322  ·  GRAND DEMO DAY  ·  PERANCANGAN PRODUK AI UNTUK PERTANIAN",
               ukuran=12, tebal=True, warna=KUNING)
    kotak_teks(s, 0.9, 1.28, 11.5, 1.15, "PupukPintar", ukuran=54, tebal=True, warna=PUTIH, font=F_JUDUL)
    garis_kuning(s, 0.92, 2.42, 2.6, 0.06)
    kotak_teks(s, 0.9, 2.72, 8.6, 0.95,
               "Membantu petani padi dan jagung mengetahui dosis pupuk N-P-K yang tepat\nuntuk lahannya sendiri, bukan menebak dari kebiasaan tetangga",
               ukuran=17, warna=ABU_TERANG, baris=1.25)
    kotak_teks(s, 0.9, 3.95, 9.2, 1.0,
               "Kelompok 14  |  Topik: Rekomendasi Dosis Pupuk Presisi per Lahan (kelanjutan audit SAFRONS)\n"
               "Irgi Setiawan (M0405241018)  ·  Syarif Abdullah Assagaf (M0405241033)  ·  Thogianna A. M. Sinaga (M0405241077)\n"
               "Ilmu Komputer IPB University  ·  Semester Ganjil 2026/2027",
               ukuran=12, warna=RGBColor(0xC9, 0xD3, 0xE0), baris=1.4)

    kartu(s, 0.9, 5.05, 7.3, 1.5, warna_isi=RGBColor(0x14, 0x2C, 0x50), garis=RGBColor(0x3A, 0x52, 0x7C), radius=0.1)
    kotak_teks(s, 1.12, 5.22, 1.6, 0.3, "COBA SENDIRI", ukuran=10.5, tebal=True, warna=KUNING)
    kotak_teks(s, 1.12, 5.55, 6.9, 0.9,
               "Aplikasi: http://127.0.0.1:8000 (jalankan python server.py sesuai README)\n"
               "GitHub: github.com/irgidev/pupukpintar   ·   Figma: bit.ly/figma-pupukpintar",
               ukuran=11, warna=PUTIH, baris=1.35)
    qr = s.shapes.add_picture(os.path.join(SINI, "..", "qr_repo.png"), Inches(9.05), Inches(4.98), height=Inches(1.62))
    qr.line.color.rgb = PUTIH
    qr.line.width = Pt(2)
    kotak_teks(s, 9.05, 6.62, 2.2, 0.25, "Pindai ke repositori", ukuran=9.5, warna=ABU_TERANG, rata=PP_ALIGN.CENTER)
    catatan(s, "SLIDE 1 SAMPUL (30 detik). Sampaikan tagline satu kalimat lalu langsung ke masalah. "
               "QR mengarah ke repositori publik berisi aplikasi, PoC, pengujian, laporan, dan presentasi. "
               "Aplikasi demo berjalan lokal tanpa akun, cara menjalankannya ada di README.")
    return s


# ======================================================================
# SLIDE 2 MASALAH DAN PENGGUNA
# ======================================================================
def slide2():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "MASALAH DAN PENGGUNA", "Masalah nyata, pengguna nyata",
                  "KRITERIA: BUSINESS VIABILITY", 2)

    kartu(s, 0.55, 2.15, 6.55, 1.95, warna_isi=HIJAU_MUDA_KARTU, radius=0.06,
          judul="PROBLEM STATEMENT", judul_warna=NAVY,
          isi="Petani padi dan jagung kecil di Bogor membutuhkan cara cepat, murah, dan mudah untuk mengetahui dosis pupuk "
              "N-P-K yang tepat untuk lahannya sendiri, karena kondisi hara antarpetak berbeda dan uji tanah laboratorium "
              "sulit dijangkau, sehingga dosis sering salah, biaya membengkak, dan hasil panen tidak optimal.",
          isi_ukuran=12.5)

    kartu(s, 0.55, 4.3, 6.55, 2.45, radius=0.06, judul="PERSONA UTAMA (kandidat, divalidasi saat pilot)",
          judul_warna=NAVY,
          isi="Pak Wandi, 41 tahun, petani padi dan jagung anggota poktan di Cibinong, lahan 0,5 sampai 1 ha\n"
              "Tujuan: menekan biaya pupuk tanpa menurunkan hasil\n"
              "Kendala: dosis mengikuti kebiasaan tetangga, uji lab dianggap mahal dan ribet\n"
              "Perangkat dan sinyal: Android jadul, kuota terbatas, sinyal memadai di rumah dan kios saprodi\n"
              "Sumber: profil pengguna LKP-P2 dan pengamatan audit LKP-P1",
          isi_ukuran=11.5)

    kartu(s, 7.35, 2.15, 5.43, 2.15, warna_isi=PUTIH, garis=ABU_TERANG, radius=0.06,
          isi="0", judul=None, isi_ukuran=44, isi_rata=PP_ALIGN.CENTER, isi_warna=BIRU)
    kotak_teks(s, 7.55, 3.55, 5.03, 0.7,
               "angka dosis yang keluar dari aplikasi peta hara\nyang kami audit (temuan audit LKP-P1 kelompok 14)",
               ukuran=11, warna=ABU, rata=PP_ALIGN.CENTER, baris=1.15)

    kartu(s, 7.35, 4.5, 5.43, 2.25, warna_isi=PUTIH, garis=ABU_TERANG, radius=0.06,
          isi="Rp 150 rb", isi_ukuran=40, isi_rata=PP_ALIGN.CENTER, isi_warna=BIRU)
    kotak_teks(s, 7.55, 5.9, 5.03, 0.75,
               "perkiraan biaya satu sampel uji tanah laboratorium\n(asumsi tim, dikonfirmasi saat pilot)",
               ukuran=11, warna=ABU, rata=PP_ALIGN.CENTER, baris=1.15)

    catatan(s, "SLIDE 2 MASALAH DAN PENGGUNA (1 sampai 1,5 menit). Satu masalah saja. "
               "Dua angka dampak punya sumber yang bisa dijelaskan bila ditanya: nol angka dosis dari audit LKP-P1 atas SAFRONS, "
               "biaya uji lab adalah asumsi tim yang jujur ditandai. Persona masih kandidat dan kejujurannya disampaikan.")
    return s


# ======================================================================
# SLIDE 3 SOLUSI DAN PENDEKATAN AI
# ======================================================================
def slide3():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "SOLUSI DAN PENDEKATAN AI", "Solusi AI kami dan cara kerjanya",
                  "KRITERIA: FUNCTIONALITY & AI INTEGRATION", 3)

    kartu(s, 0.55, 2.12, 12.23, 0.78, warna_isi=BIRU, radius=0.1,
          isi="Produk kami adalah PupukPintar, yaitu aplikasi web berbasis machine learning yang membantu petani padi dan jagung "
              "untuk menghitung dosis pupuk N-P-K spesifik per lahan sehingga biaya pupuk terkendali dan keputusan tetap terverifikasi penyuluh.",
          isi_ukuran=12.5, isi_warna=PUTIH)

    x_list = [0.55, 3.72, 6.89, 10.06]
    w = 2.72
    isi_kartu = [
        ("INPUT", "Kondisi lahan: pH, N, P, K,\ntekstur, komoditas, target\nhasil, luas, musim\n(pilih unit di peta atau uji tanah)"),
        ("INTELLIGENCE", "Random Forest Regressor\n300 pohon + keyakinan\nantarpohon + guardrail rentang\nPermentan + aturan Balittanah"),
        ("UX", "Kartu dosis kg/ha dan kg\nper petak, badge keyakinan,\nestimasi biaya, paket modal,\npenjelasan sederhana"),
        ("VALUE", "Dosis tepat per lahan,\npotensi hemat biaya pupuk,\nkeputusan aman lewat\nverifikasi penyuluh"),
    ]
    for i, (judul, isi) in enumerate(isi_kartu):
        kartu(s, x_list[i], 3.1, w, 2.0, radius=0.08, judul=judul, judul_warna=NAVY, judul_ukuran=12.5,
              isi=isi, isi_ukuran=10.5)
        if i < 3:
            arah = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x_list[i] + w + 0.06), Inches(3.95), Inches(0.3), Inches(0.3))
            arah.fill.solid()
            arah.fill.fore_color.rgb = KUNING
            arah.line.fill.background()
            arah.shadow.inherit = False

    kartu(s, 0.55, 5.35, 12.23, 1.42, warna_isi=PUTIH_SUSU, garis=ABU_TERANG, radius=0.06,
          judul="PENDEKATAN AI YANG BENAR-BENAR DIPAKAI", judul_warna=NAVY, judul_ukuran=11.5)
    kotak_teks(s, 0.75, 5.72, 5.6, 0.9,
               "[v] Rule-based (guardrail dan peringatan)\n[v] Predictive (inti: regresi dosis N-P-K)\n[ ] Generative (penjelasan memakai templat)     [ ] Agentic (ditunda)",
               ukuran=11.5, baris=1.35)
    kotak_teks(s, 6.6, 5.72, 6.0, 0.9,
               "Alasan: data latih berlabel dari tabel resmi dan target berupa angka kontinu sehingga regresi paling cocok, "
               "aturan menjaga keluaran tetap patuh rekomendasi resmi, dan templat menghindari risiko angka dikarang.",
               ukuran=10.5, warna=ABU, baris=1.2)

    catatan(s, "SLIDE 3 SOLUSI DAN PENDEKATAN AI (1 sampai 1,5 menit). Jelaskan alur Input, Intelligence, UX, Value dengan satu contoh "
               "konkret: pH 5,4 dan P rendah memasuki model, keluar dosis 217-83-51 kg/ha dengan keyakinan 81 persen. "
               "Jawab pertanyaan penilai: kenapa random forest, bukan yang lain (non-linear, feature importance, tanpa GPU, mudah dijelaskan).")
    return s


# ======================================================================
# SLIDE 4 DEMO
# ======================================================================
def slide4():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "DEMO PRODUK", "Demo: dari masukan sampai hasil AI",
                  "KRITERIA: FUNCTIONALITY & AI INTEGRATION", 4)

    kotak_teks(s, 0.55, 2.1, 3.3, 0.4, "Layar hasil untuk padi, 0,75 ha (F-03, F-04)", ukuran=10.5, warna=ABU)
    w = tambah_tangkapan(s, "09-hasil-rekomendasi.png", 0.55, 2.5, 4.55)
    # bingkai tipis
    bing = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(2.5), Inches(w), Inches(4.55))
    bing.fill.background()
    bing.line.color.rgb = ABU
    bing.line.width = Pt(1)
    bing.shadow.inherit = False

    langkah = [
        ("1", "Pengguna melakukan", "Cari daerahnya lewat pencarian, pilih unit lahannya di peta (peta membesarkan unit), atau masukkan hasil uji tanah, lalu pilih komoditas dan target hasil"),
        ("2", "AI memproses", "Random Forest memprediksi dosis N-P-K, menghitung keyakinan dari sebaran antarpohon, guardrail mengunci rentang aman (p95 API 87 ms)"),
        ("3", "Pengguna menerima", "Dosis kg/ha dan kg per petak, estimasi biaya, tiga paket modal, keyakinan 81%, penjelasan, dan disclaimer"),
    ]
    y = 2.5
    for nomor, judul, isi in langkah:
        kartu(s, 5.3, y, 7.48, 1.02, radius=0.08)
        pil(s, 5.48, y + 0.27, 0.48, 0.48, nomor, latar=BIRU, warna_teks=PUTIH, ukuran=15)
        kotak_teks(s, 6.15, y + 0.12, 6.5, 0.3, judul, ukuran=11.5, tebal=True, warna=NAVY)
        kotak_teks(s, 6.15, y + 0.42, 6.45, 0.55, isi, ukuran=10.5, warna=ABU, baris=1.12)
        y += 1.17

    kartu(s, 5.3, 6.05, 7.48, 1.0, warna_isi=KUNING_MUDA, radius=0.08,
          judul="RENCANA CADANGAN", judul_warna=NAVY, judul_ukuran=11,
          isi="Jika koneksi gagal, tangkapan layar lengkap setiap langkah ada di docs/tangkapan-layar repositori, "
              "lalu alur diulang setelah koneksi pulih. Data demo pasti berhasil: padi, pH 5,4, target 6 t/ha.",
          isi_ukuran=10.5)

    catatan(s, "SLIDE 4 DEMO (2 sampai 3 menit, bagian terpenting). Demokan langsung alur tiga ketukan: pilih petak, "
               "Hitung Rekomendasi, hasil. Sebut ID fitur F-03 dan F-04 agar cocok dengan laporan. "
               "Siapkan akun tidak diperlukan karena tanpa login. Video cadangan menyusul, sementara itu tangkapan layar lengkap ada di repositori.")
    return s


# ======================================================================
# SLIDE 5 AI UX DAN KETIDAKPASTIAN
# ======================================================================
def slide5():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "AI UX DAN KETIDAKPASTIAN", "Bagaimana produk menangani ketidakpastian AI",
                  "KRITERIA: AI UX & UNCERTAINTY HANDLING", 5)

    x = 0.55
    w = 4.02
    # kartu YAKIN
    kartu(s, x, 2.12, w, 3.9, radius=0.06, judul="YAKIN  (>= 85%)", judul_warna=NAVY, judul_ukuran=12.5)
    pil(s, x + 0.14, 2.6, 1.35, 0.4, "HIJAU", latar=RGBColor(0xE4, 0xEE, 0xE6), warna_teks=NAVY, ukuran=10)
    w_img = tambah_tangkapan(s, "15-hasil-jagung.png", x + 1.62, 2.62, 2.55)
    kotak_teks(s, x + 0.14, 5.3, w - 0.28, 0.7,
               "Pesan: Keyakinan 95% (Yakin), kartu dosis plus sub-label rentang aman resmi\n"
               "Aksi: tetap disertai disclaimer dan tombol verifikasi penyuluh",
               ukuran=10, warna=ABU, baris=1.18)

    # kartu RAGU
    x2 = x + w + 0.09
    kartu(s, x2, 2.12, w, 3.9, radius=0.06, judul="RAGU  (70 - 85%)", judul_warna=NAVY, judul_ukuran=12.5)
    pil(s, x2 + 0.14, 2.6, 1.35, 0.4, "KUNING", latar=RGBColor(0xF9, 0xEE, 0xD6), warna_teks=RGBColor(0x7A, 0x54, 0x10), ukuran=10)
    w_img2 = tambah_tangkapan(s, "09-hasil-rekomendasi.png", x2 + 1.62, 2.62, 2.55)
    kotak_teks(s, x2 + 0.14, 5.3, w - 0.28, 0.7,
               "Pesan: Keyakinan 81% (Cukup yakin), angka tampil dengan rentang aman\n"
               "Aksi: anjuran cek ulang dan verifikasi penyuluh diperkuat",
               ukuran=10, warna=ABU, baris=1.18)

    # kartu DI LUAR DOMAIN / GAGAL
    x3 = x2 + w + 0.09
    kartu(s, x3, 2.12, w, 3.9, radius=0.06, judul="LUAR SEBARAN / GAGAL", judul_warna=NAVY, judul_ukuran=12.5)
    pil(s, x3 + 0.14, 2.6, 1.35, 0.4, "MERAH", latar=RGBColor(0xF6, 0xE0, 0xDD), warna_teks=RGBColor(0xA3, 0x35, 0x2C), ukuran=10)
    w_img3 = tambah_tangkapan(s, "14-hasil-luar-sebaran.png", x3 + 1.62, 2.62, 2.55)
    kotak_teks(s, x3 + 0.14, 5.3, w - 0.28, 0.7,
               "Pesan: kondisi di luar sebaran data latih, angka tidak ditampilkan\n"
               "Aksi: diarahkan ke uji tanah lab atau penyuluh",
               ukuran=10, warna=ABU, baris=1.18)

    kartu(s, 0.55, 6.2, 12.23, 0.82, warna_isi=BIRU, radius=0.1,
          isi="Human-in-the-loop: menjalankan dosis pupuk diserahkan ke petani setelah verifikasi penyuluh, "
              "lewat tombol Kirim ke Penyuluh pada setiap hasil dan panel verifikasi pada Papan Penyuluhan.",
          isi_ukuran=12, isi_warna=PUTIH)

    catatan(s, "SLIDE 5 AI UX DAN KETIDAKPASTIAN (1 sampai 1,5 menit). Ambang persentase sama dengan Bab 4.4 laporan "
               "(0,70 dan 0,85, ditetapkan sebelum pengujian). Jelaskan alasan bentuk penyajian keyakinan: persen untuk takaran, "
               "kata kategori untuk petani awam, warna terbaca sekali pandang. Tangkapan layar semuanya nyata dari aplikasi.")
    return s


# ======================================================================
# SLIDE 6 HASIL PENGUJIAN
# ======================================================================
def slide6():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "HASIL PENGUJIAN", "Bukti kualitas: apakah MVQ tercapai?",
                  "KRITERIA: FUNCTIONALITY & AI UX", 6)

    baris_mvq = [
        ["Dimensi", "Ambang", "Hasil", "Lulus?"],
        ["Agreement pakar", "85-90%", "95,2% (holdout 1.200 baris)", "Ya"],
        ["Waktu respons", "< 5 detik", "p95 API 87 ms", "Ya"],
        ["Guardrail rentang aman", "0 pelanggaran", "45 kombinasi ekstrem, semua terkunci", "Ya"],
        ["Explainability", "100% hasil", "Penjelasan dan keyakinan di semua jawaban", "Ya"],
        ["Keamanan kasus ragu", "100% ke jalur aman", "Angka disembunyikan, arahan uji lab", "Ya"],
        ["Kepuasan petani", ">= 4/5", "Belum diukur, menunggu pilot poktan", "Belum"],
    ]
    tbl = s.shapes.add_table(len(baris_mvq), 4, Inches(0.55), Inches(2.12), Inches(7.9), Inches(3.3)).table
    tbl.columns[0].width = Inches(2.0)
    tbl.columns[1].width = Inches(1.35)
    tbl.columns[2].width = Inches(3.2)
    tbl.columns[3].width = Inches(1.35)
    for r, row in enumerate(baris_mvq):
        for c, teks in enumerate(row):
            sel = tbl.cell(r, c)
            sel.text = teks
            par = sel.text_frame.paragraphs[0]
            par.line_spacing = 1.05
            run = par.runs[0]
            run.font.size = Pt(10.5)
            run.font.name = F_TEKS
            run.font.bold = r == 0
            run.font.color.rgb = PUTIH if r == 0 else TINTA
            sel.fill.solid()
            sel.fill.fore_color.rgb = BIRU if r == 0 else (PUTIH_SUSU if r % 2 else PUTIH)

    kartu(s, 0.55, 5.75, 2.5, 1.35, isi="18/18", isi_ukuran=30, isi_rata=PP_ALIGN.CENTER, isi_warna=BIRU)
    kotak_teks(s, 0.65, 6.6, 2.3, 0.45, "langkah uji antarmuka lulus, tanpa galat konsol", ukuran=9.5, warna=ABU, rata=PP_ALIGN.CENTER, baris=1.1)
    kartu(s, 3.25, 5.75, 2.5, 1.35, isi="95,2%", isi_ukuran=30, isi_rata=PP_ALIGN.CENTER, isi_warna=BIRU)
    kotak_teks(s, 3.35, 6.6, 2.3, 0.45, "agreement rekomendasi pada data uji terpisah", ukuran=9.5, warna=ABU, rata=PP_ALIGN.CENTER, baris=1.1)
    kartu(s, 5.95, 5.75, 2.5, 1.35, isi="87 ms", isi_ukuran=30, isi_rata=PP_ALIGN.CENTER, isi_warna=BIRU)
    kotak_teks(s, 6.05, 6.6, 2.3, 0.45, "latensi p95 API dari 30 permintaan", ukuran=9.5, warna=ABU, rata=PP_ALIGN.CENTER, baris=1.1)

    kartu(s, 8.65, 2.12, 4.13, 4.98, radius=0.06, judul="TEMUAN TERBESAR DAN PERBAIKAN", judul_warna=NAVY, judul_ukuran=11.5,
          isi="1. Keyakinan pita tengah belum terkalibrasi: kelompok Cukup yakin hanya mencapai agreement 42,9% "
              "(jarang, 1,2% kasus). Perbaikan: kategori sedang selalu disertai rentang aman dan anjuran verifikasi.\n\n"
              "2. Badge keyakinan terpotong pada layar 390 px saat uji. Diperbaiki, kini berada pada baris sendiri.\n\n"
              "3. Data uji terpisah dari data latih: holdout 20% dengan seed berbeda, tidak disentuh saat pemilihan model.\n\n"
              "Kejujuran: kepuasan petani belum diukur dan kami laporkan apa adanya.",
          isi_ukuran=10.5)

    catatan(s, "SLIDE 6 BUKTI KUALITAS (1 sampai 1,5 menit). Ambang MVQ sama dengan Bab 4.4 dan ditetapkan sebelum pengujian. "
               "Sebut siapa penguji: 12 pengujian pytest dan 18 langkah Playwright oleh tim, dan katakan jujur bahwa petani sasaran "
               "belum menjadi penguji. Penilai lebih menghargai pelaporan temuan buruk daripada angka sempurna.")
    return s


# ======================================================================
# SLIDE 7 EKONOMI AI
# ======================================================================
def slide7():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "EKONOMI AI DAN BISNIS", "Layak secara finansial: biaya dan model bisnis",
                  "KRITERIA: BUSINESS VIABILITY & TOKEN ECONOMICS", 7)

    kartu(s, 0.55, 2.12, 7.9, 0.85, warna_isi=BIRU, radius=0.08,
          isi="Produk non-LLM: biaya per prediksi = biaya server per bulan ÷ jumlah prediksi per bulan\n"
              "Sumber harga: asumsi VPS 1 CPU 1 GB Rp 90.000/bulan (asumsi tim, belum ada tagihan nyata karena demo lokal)",
          isi_ukuran=11, isi_warna=PUTIH)

    baris = [
        ["Skenario", "Petani", "Prediksi/bln", "Biaya bln", "Per prediksi"],
        ["Konservatif (1 poktan)", "25", "125", "Rp 90.000", "Rp 720"],
        ["Realistis (4 poktan)", "100", "500", "Rp 90.000", "Rp 180"],
        ["Optimistis (20 poktan)", "500", "2.500", "Rp 180.000", "Rp 72"],
    ]
    tbl = s.shapes.add_table(len(baris), 5, Inches(0.55), Inches(3.15), Inches(7.9), Inches(2.0)).table
    tbl.columns[0].width = Inches(2.5)
    tbl.columns[1].width = Inches(1.1)
    tbl.columns[2].width = Inches(1.5)
    tbl.columns[3].width = Inches(1.4)
    tbl.columns[4].width = Inches(1.4)
    for r, row in enumerate(baris):
        for c, teks in enumerate(row):
            sel = tbl.cell(r, c)
            sel.text = teks
            run = sel.text_frame.paragraphs[0].runs[0]
            run.font.size = Pt(10.5)
            run.font.name = F_TEKS
            run.font.bold = r == 0
            run.font.color.rgb = PUTIH if r == 0 else TINTA
            sel.fill.solid()
            sel.fill.fore_color.rgb = BIRU if r == 0 else (PUTIH_SUSU if r % 2 else PUTIH)
    kotak_teks(s, 0.55, 5.3, 7.9, 0.6,
               "Pembanding: satu uji tanah lab (asumsi Rp 150.000) setara 208 prediksi pada skenario konservatif. "
               "Strategi hemat: model 300 pohon tanpa GPU, penjelasan templat tanpa LLM (biaya token nol), data peta statis.",
               ukuran=10.5, warna=ABU, baris=1.2)

    kartu(s, 8.65, 2.12, 4.13, 3.5, radius=0.06, judul="MODEL BISNIS", judul_warna=NAVY, judul_ukuran=12,
          isi="Siapa membayar\nPilot gratis, kelak poktan atau koperasi berlangganan\n\n"
              "Skema dan harga (rencana)\nIuran poktan Rp 25.000 per bulan untuk rekap kebutuhan anggota\n\n"
              "Titik impas\nRp 90.000 ÷ Rp 25.000 = 3,6, dibulatkan 4 poktan\n\n"
              "Bukti kesediaan bayar\nBelum ada, jujur kami tandai sebagai asumsi untuk divalidasi saat pilot",
          isi_ukuran=10.5)

    kartu(s, 8.65, 5.8, 4.13, 1.25, warna_isi=PUTIH_SUSU, garis=ABU_TERANG, radius=0.06,
          judul="BIAYA SELAIN SERVER", judul_warna=NAVY, judul_ukuran=11,
          isi="Pelatihan ulang model tiap musim: Rp 0 (4 detik di laptop, tanpa GPU)\nDomain saat dipublikasikan: sekitar Rp 200.000/tahun",
          isi_ukuran=10)

    catatan(s, "SLIDE 7 TOKEN ECONOMICS (1 sampai 1,5 menit). Produk tanpa LLM sehingga rumus biaya token diganti biaya server per prediksi "
               "sesuai panduan template. Tiga skenario dihitung dengan rumus di slide. Titik impas empat poktan pada harga iuran yang "
               "masih asumsi. Jawab pertanyaan siapa yang membayar dengan jujur: petani tidak dibebani.")
    return s


# ======================================================================
# SLIDE 8 GOVERNANCE
# ======================================================================
def slide8():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "GOVERNANCE DAN KEAMANAN", "Aman dan bertanggung jawab bagi petani",
                  "KRITERIA: GOVERNANCE & SAFETY", 8)

    baris = [
        ["Risiko", "Peluang", "Dampak", "Mitigasi yang bisa ditunjukkan di aplikasi"],
        ["Prediksi keliru di luar sebaran latih", "S", "T", "Guardrail rentang resmi, penanda luar sebaran, angka disembunyikan (teruji)"],
        ["Ketergantungan berlebih pada AI", "S", "T", "Badge keyakinan, kata kategori, disclaimer permanen, jalur penyuluh"],
        ["Salah paham satuan", "S", "S", "Layar hasil menampilkan kg/ha dan kg per petak sekaligus dengan luas tertulis"],
    ]
    tbl = s.shapes.add_table(len(baris), 4, Inches(0.55), Inches(2.12), Inches(12.23), Inches(2.3)).table
    tbl.columns[0].width = Inches(3.3)
    tbl.columns[1].width = Inches(1.0)
    tbl.columns[2].width = Inches(1.0)
    tbl.columns[3].width = Inches(6.93)
    for r, row in enumerate(baris):
        for c, teks in enumerate(row):
            sel = tbl.cell(r, c)
            sel.text = teks
            run = sel.text_frame.paragraphs[0].runs[0]
            run.font.size = Pt(10.5)
            run.font.name = F_TEKS
            run.font.bold = r == 0
            run.font.color.rgb = PUTIH if r == 0 else TINTA
            sel.fill.solid()
            sel.fill.fore_color.rgb = BIRU if r == 0 else (PUTIH_SUSU if r % 2 else PUTIH)

    kartu(s, 0.55, 4.7, 6.0, 2.25, radius=0.06, judul="GUARDRAIL DAN DISCLAIMER", judul_warna=NAVY, judul_ukuran=11.5,
          isi="Enam guardrail terpasang dan diuji: kunci rentang Permentan, penolakan input buruk, penanda luar sebaran, "
              "ambang keyakinan 0,70, peringatan Balittanah (pengapuran, urea dibagi dua saat hujan), disclaimer permanen.\n\n"
              "Teks disclaimer persis: \"Rekomendasi awal dari model, bukan pengganti uji tanah laboratorium. "
              "Verifikasi penyuluh sebelum pembelian pupuk.\"",
          isi_ukuran=10.5)

    kartu(s, 6.78, 4.7, 6.0, 2.25, radius=0.06, judul="PRIVASI DAN PERSETUJUAN", judul_warna=NAVY, judul_ukuran=11.5,
          isi="Data lahan disimpan di perangkat petani (localStorage), tidak ada server penyimpanan koordinat.\n\n"
              "Persetujuan saat onboarding: \"Data lahan Anda dipakai untuk rekomendasi pribadi dan perbaikan model. "
              "Identitas disamarkan dan bisa dihapus kapan saja dari halaman Profil.\"\n\n"
              "Profil menyediakan saklar tolak pelatihan model dan tombol hapus semua data.",
          isi_ukuran=10.5)

    catatan(s, "SLIDE 8 GOVERNANCE (1 sampai 1,5 menit). Tiga risiko paling nyata untuk produk ini, semua mitigasi berupa elemen "
               "aplikasi yang bisa ditunjukkan langsung. Sebut disclaimer persis seperti tampil. "
               "Siapkan jawaban: bila AI salah dan petani sudah bertindak, tanggung jawab akhir ada pada keputusan manusia "
               "setelah verifikasi penyuluh, dan kasus ragu tidak pernah ditampilkan sebagai angka.")
    return s


# ======================================================================
# SLIDE 9 ADOPSI
# ======================================================================
def slide9():
    s = slide_baru(LAYOUT_KONTEN)
    kepala_konten(s, "ADOPSI DAN RENCANA LANJUTAN", "Dari prototipe ke pengguna nyata",
                  "KRITERIA: BUSINESS VIABILITY", 9)

    tahap = [
        ("PILOT", "Satu poktan di Bogor, sekitar 25 petani, musim hujan berikutnya"),
        ("PERLUASAN", "Empat sampai lima poktan, sekitar 100 petani, model dilatih ulang dengan data lapangan"),
        ("SKALA", "Kerja sama koperasi atau dinas, perluasan wilayah dan komoditas"),
    ]
    x = 0.55
    for i, (judul, isi) in enumerate(tahap):
        kartu(s, x + i * 4.13, 2.12, 3.95, 1.55, radius=0.08, judul=judul, judul_warna=NAVY, judul_ukuran=12.5,
              isi=isi, isi_ukuran=10.5)
        if i < 2:
            arah = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + i * 4.13 + 3.98), Inches(2.75), Inches(0.3), Inches(0.3))
            arah.fill.solid()
            arah.fill.fore_color.rgb = KUNING
            arah.line.fill.background()
            arah.shadow.inherit = False

    kartu(s, 0.55, 3.95, 6.0, 2.9, radius=0.06, judul="ROADMAP: FITUR YANG DITUNDA", judul_warna=NAVY, judul_ukuran=11.5,
          isi="Draf RDKK otomatis, butuh akumulasi data anggota poktan yang baru ada setelah pilot\n\n"
              "Kalender pemupukan pribadi, butuh riwayat petak lintas musim\n\n"
              "Diagnosis hama dari foto, butuh dataset citra dan model visi yang terpisah\n\n"
              "Rilis APK Android (Flutter), menunggu alur terkonfirmasi petani",
          isi_ukuran=10.5)

    kartu(s, 6.78, 3.95, 6.0, 2.9, radius=0.06, judul="KETERBATASAN DAN PEMBELAJARAN", judul_warna=NAVY, judul_ukuran=11.5,
          isi="Data latih masih proxy tabel resmi, validasi lapangan belum selesai\n\n"
              "Penguji usability masih tim, petani sasaran menyusul pada pilot\n\n"
              "Pelajaran terpenting: model yang bagus pada data proxy belum berarti benar di lapangan, "
              "jadi guardrail dan jalur manusia kami rancang sejak awal\n\n"
              "Umpan balik setelah rilis lewat panel verifikasi penyuluh dan kunjungan poktan tiap dua pekan",
          isi_ukuran=10.5)

    catatan(s, "SLIDE 9 ADOPSI (1 menit). Mitra poktan dan penyuluh belum dihubungi dan kami sampaikan jujur beserta rencana kontaknya. "
               "Sampaikan keterbatasan sebagai kematangan, bukan kelemahan. Setiap fitur ditunda punya alasan dan ketergantungan yang jelas.")
    return s


# ======================================================================
# SLIDE 10 PENUTUP
# ======================================================================
def slide10():
    s = slide_baru(LAYOUT_CLOSING)
    kotak_teks(s, 0.9, 0.62, 11.5, 0.35, "RINGKASAN: EMPAT KRITERIA, SATU PRODUK", ukuran=12, tebal=True, warna=KUNING)
    kotak_teks(s, 0.9, 1.1, 11.5, 0.9, "Terima Kasih", ukuran=40, tebal=True, warna=PUTIH, font=F_JUDUL)
    garis_kuning(s, 0.92, 2.05, 2.2, 0.05)

    baris_kriteria = [
        ("Functionality & AI Integration", "Agreement 95,2% pada data uji terpisah, latensi p95 87 ms, guardrail rentang resmi lulus seluruh uji"),
        ("AI UX & Uncertainty Handling", "Tiga kategori keyakinan berkode warna, kasus ragu dan luar sebaran tidak pernah menampilkan angka"),
        ("Business Viability & Token Economics", "Biaya Rp 180 per prediksi pada skenario realistis tanpa biaya token, titik impas 4 poktan"),
        ("Governance & Safety", "Enam guardrail teruji, consent dan penghapusan data di aplikasi, keputusan akhir tetap pada manusia"),
    ]
    y = 2.5
    for judul, bukti in baris_kriteria:
        kotak_teks(s, 0.95, y, 4.6, 0.4, judul, ukuran=13, tebal=True, warna=KUNING_MUDA)
        kotak_teks(s, 5.6, y, 7.0, 0.62, bukti, ukuran=11.5, warna=PUTIH, baris=1.15)
        garis_abu = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(y + 0.58), Inches(11.4), Inches(0.012))
        garis_abu.fill.solid()
        garis_abu.fill.fore_color.rgb = RGBColor(0x3A, 0x52, 0x7C)
        garis_abu.line.fill.background()
        garis_abu.shadow.inherit = False
        y += 0.78

    kartu(s, 0.9, 5.95, 7.3, 1.1, warna_isi=RGBColor(0x14, 0x2C, 0x50), garis=RGBColor(0x3A, 0x52, 0x7C), radius=0.1)
    kotak_teks(s, 1.12, 6.1, 1.5, 0.3, "TAUTAN", ukuran=10.5, tebal=True, warna=KUNING)
    kotak_teks(s, 1.12, 6.4, 6.9, 0.6,
               "GitHub: github.com/irgidev/pupukpintar   ·   Figma: bit.ly/figma-pupukpintar\n"
               "Aplikasi demo: http://127.0.0.1:8000 (README repositori)",
               ukuran=11, warna=PUTIH, baris=1.3)
    kotak_teks(s, 8.5, 6.3, 4.2, 0.4, "Tanya jawab  ·  PupukPintar  ·  Kelompok 14", ukuran=12, warna=ABU_TERANG, rata=PP_ALIGN.RIGHT)

    catatan(s, "SLIDE 10 PENUTUP (30 detik plus tanya jawab). Satu kalimat bukti per kriteria, angkanya sama dengan slide sebelumnya. "
               "Siapkan jawaban empat pertanyaan umum: mengapa random forest, apa yang terjadi bila AI salah, berapa biaya per bulan, "
               "siapa yang akan membayar. Biarkan slide ini tampil selama tanya jawab.")
    return s


# ======================================================================
# perakitan
# ======================================================================
def bangun():
    hapus_semua_slide()
    slide1()
    slide2()
    slide3()
    slide4()
    slide5()
    slide6()
    slide7()
    slide8()
    slide9()
    slide10()
    prs.save(KELUAR)
    print("tersimpan:", KELUAR)


if __name__ == "__main__":
    bangun()
