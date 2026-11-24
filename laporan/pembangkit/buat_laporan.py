# -*- coding: utf-8 -*-
"""
Pembangkit Laporan Akhir Produk AI (PPKBP, Kelompok 14, PupukPintar).

Menghasilkan Laporan_Akhir_PupukPintar_Kelompok14.docx mengikuti struktur
Template_Laporan_Akhir_Produk_AI.docx: ringkasan eksekutif, 12 bab,
daftar pustaka, dan lampiran A sampai E.

Aturan penulisan yang dipatuhi skrip ini:
- tanpa em dash, tanpa titik koma pada kalimat penjelasan,
- huruf tebal hanya untuk judul, subjudul, dan kepala tabel,
- angka memakai koma desimal Indonesia,
- setiap klaim punya bukti (gambar, tabel, uji, atau berkas di repositori).

Jalankan dari folder laporan/pembangkit:
    python buat_laporan.py [jalur-folder-repo]
"""

import json
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

REPO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

GAMBAR = os.path.join(REPO, "docs")
LAYAR = os.path.join(GAMBAR, "tangkapan-layar")
WIRE = os.path.join(GAMBAR, "wireframe")

# ----------------------------------------------------------------------
# data angka nyata dari artefak pengujian
# ----------------------------------------------------------------------
with open(os.path.join(REPO, "app", "backend", "metrik_model.json"), encoding="utf-8") as f:
    METRIK = json.load(f)
with open(os.path.join(REPO, "tests", "hasil_evaluasi_tambahan.json"), encoding="utf-8") as f:
    TAMBAHAN = json.load(f)
with open(os.path.join(REPO, "poc", "hasil_poc.json"), encoding="utf-8") as f:
    POC = json.load(f)

CV = METRIK["cv"]
HOLD = METRIK["holdout"]
HARA_L = {"Dosis_N": "N", "Dosis_P": "P", "Dosis_K": "K"}

TAUTAN = {
    "github": "https://github.com/irgidev/pupukpintar",
    "github_poc": "https://github.com/irgidev/pupukpintar-poc",
    "figma": "https://www.figma.com/design/rSkPUlILq9yMteqXRwDBHF/PupukPintar?node-id=0-1",
    "app": "http://127.0.0.1:8000 (demo lokal, cara menjalankan ada di README repositori)",
}

# ----------------------------------------------------------------------
# kerangka dokumen dan gaya
# ----------------------------------------------------------------------
doc = Document()

# ukuran halaman A4 dan margin 2,5 cm
for s in doc.sections:
    s.page_width = Cm(21)
    s.page_height = Cm(29.7)
    s.left_margin = Cm(2.5)
    s.right_margin = Cm(2.5)
    s.top_margin = Cm(2.5)
    s.bottom_margin = Cm(2.5)


def atur_gaya():
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    for nama, ukuran, sebelum in (("Heading 1", 14, 18), ("Heading 2", 12.5, 12), ("Heading 3", 12, 8)):
        gaya = doc.styles[nama]
        gaya.font.name = "Times New Roman"
        gaya.font.size = Pt(ukuran)
        gaya.font.bold = True
        gaya.font.color.rgb = RGBColor(0, 0, 0)
        gaya.paragraph_format.space_before = Pt(sebelum)
        gaya.paragraph_format.space_after = Pt(6)
        gaya.paragraph_format.line_spacing = 1.3

atur_gaya()


def pasang_nomor_halaman():
    """Nomor halaman pada footer tengah memakai field PAGE."""
    for section in doc.sections:
        par = section.footer.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = par.add_run()
        mulai = OxmlElement("w:fldChar")
        mulai.set(qn("w:fldCharType"), "begin")
        teks = OxmlElement("w:instrText")
        teks.set(qn("xml:space"), "preserve")
        teks.text = "PAGE"
        akhir = OxmlElement("w:fldChar")
        akhir.set(qn("w:fldCharType"), "end")
        run._r.append(mulai)
        run._r.append(teks)
        run._r.append(akhir)
        run.font.size = Pt(10)
        run.font.name = "Times New Roman"


pasang_nomor_halaman()

HALAMAN_ISI = {}  # diisi pada pass kedua untuk daftar isi
# pass kedua: baca hasil pemindaian PDF dari pass pertama bila ada
_jalur_halaman = os.path.join(os.path.dirname(os.path.abspath(__file__)), "halaman_toi.json")
if os.path.exists(_jalur_halaman):
    with open(_jalur_halaman, encoding="utf-8") as _f:
        HALAMAN_ISI = json.load(_f)

# ----------------------------------------------------------------------
# pembantu penulisan
# ----------------------------------------------------------------------

def p(isi, rata="justify", ukuran=12, sebelum=0, sesudah=6, miring=False, gaya=None):
    par = doc.add_paragraph(style=gaya)
    par.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "tengah": WD_ALIGN_PARAGRAPH.CENTER,
                     "kiri": WD_ALIGN_PARAGRAPH.LEFT, "kanan": WD_ALIGN_PARAGRAPH.RIGHT}[rata]
    par.paragraph_format.space_before = Pt(sebelum)
    par.paragraph_format.space_after = Pt(sesudah)
    run = par.add_run(isi)
    run.font.size = Pt(ukuran)
    run.italic = miring
    return par


def bullet(isi, ukuran=12):
    par = doc.add_paragraph(style="List Bullet")
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    par.paragraph_format.line_spacing = 1.4
    par.paragraph_format.space_after = Pt(2)
    run = par.add_run(isi)
    run.font.size = Pt(ukuran)
    return par


def h1(isi):
    par = doc.add_heading(isi, level=1)
    par.paragraph_format.keep_with_next = True


def h2(isi):
    par = doc.add_heading(isi, level=2)
    par.paragraph_format.keep_with_next = True


def h3(isi):
    par = doc.add_heading(isi, level=3)
    par.paragraph_format.keep_with_next = True


def tabel(judul_tabel, kepala, baris, lebar=None, ukuran=10.5, padat=False):
    if judul_tabel:
        par_judul = p(judul_tabel, rata="kiri", ukuran=10.5, sesudah=3)
        par_judul.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(kepala))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    trPr = t.rows[0]._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))
    trPr.append(OxmlElement("w:cantSplit"))
    hdr = t.rows[0].cells
    for i, teks in enumerate(kepala):
        hdr[i].text = ""
        par = hdr[i].paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.line_spacing = 1.15
        par.paragraph_format.keep_with_next = True
        run = par.add_run(teks)
        run.bold = True
        run.font.size = Pt(ukuran)
    for b in baris:
        row_baru = t.add_row()
        trPr = row_baru._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        sel = row_baru.cells
        for i, teks in enumerate(b):
            sel[i].text = ""
            par = sel[i].paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.LEFT
            par.paragraph_format.line_spacing = 1.15
            par.paragraph_format.space_after = Pt(0)
            run = par.add_run(str(teks))
            run.font.size = Pt(ukuran)
    if lebar:
        for i, w in enumerate(lebar):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    if not padat:
        p("", sesudah=4)
    return t


def gambar(jalur, keterangan, lebar_cm=14.5):
    if not os.path.exists(jalur):
        p(f"[gambar tidak ditemukan: {jalur}]", rata="kiri", miring=True)
        return
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.space_after = Pt(2)
    run = par.add_run()
    run.add_picture(jalur, width=Cm(lebar_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    r = cap.add_run(keterangan)
    r.font.size = Pt(10.5)


def daftar_periksa(items):
    """Tabel daftar periksa bab sesuai template, diisi status jujur."""
    tabel(None, ["Butir periksa", "Status"], items, lebar=[12.5, 3.5])


def pecah_halaman():
    doc.add_page_break()


def kode(teks_json):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.LEFT
    par.paragraph_format.line_spacing = 1.0
    par.paragraph_format.space_after = Pt(8)
    par.paragraph_format.left_indent = Cm(0.8)
    run = par.add_run(teks_json)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    return par


# ======================================================================
# HALAMAN SAMPUL
# ======================================================================
def sampul():
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(0)
    par.add_run().add_picture(os.path.join(REPO, "..", "proyek_akhir", "Logo-IPB-baru1000.png"), width=Cm(3.2))

    p("LAPORAN AKHIR PRODUK", rata="tengah", ukuran=16, sebelum=4, sesudah=0)
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(0)
    run = par.add_run("Perancangan Produk Kecerdasan Buatan untuk Pertanian")
    run.font.size = Pt(12)
    p("Grand Demo Day", rata="tengah", ukuran=11, sesudah=6)

    p("PupukPintar", rata="tengah", ukuran=17, sesudah=0)
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(6)
    run = par.add_run("Rekomendasi Dosis Pupuk N, P, K Presisi per Lahan untuk Petani Padi dan Jagung di Bogor dan Sekitarnya")
    run.font.size = Pt(11)

    tabel(None, ["Item", "Keterangan"], [
        ["Nama produk", "PupukPintar"],
        ["Tagline", "Membantu petani mengetahui dosis pupuk yang tepat untuk lahannya sendiri"],
        ["Kelompok", "14"],
        ["Topik responsi", "Rekomendasi Dosis Pupuk Presisi per Lahan (kelanjutan audit SAFRONS)"],
        ["Semester / tahun ajaran", "Ganjil 2026/2027"],
    ], lebar=[4.6, 11.4], ukuran=9.5, padat=True)

    tabel("Anggota kelompok", ["No", "Nama lengkap", "NIM", "Peran utama dalam tim"], [
        ["1", "Irgi Setiawan", "M0405241018", "Model, data, dan evaluasi"],
        ["2", "Syarif Abdullah Assagaf", "M0405241033", "Server, pengujian, dan integrasi"],
        ["3", "Thogianna A. M. Sinaga", "M0405241077", "Antarmuka, desain, dan wireframe"],
    ], lebar=[0.9, 5.4, 3.1, 6.6], ukuran=9.5, padat=True)

    tabel("Tautan wajib", ["Item", "URL", "Catatan akses"], [
        ["Repositori GitHub", TAUTAN["github"], "publik, berisi aplikasi, PoC, pengujian, laporan, presentasi"],
        ["Desain Figma", TAUTAN["figma"], "wireframe low-fidelity, berisi tiga layar terpenting"],
        ["Desain high-fidelity", "docs/desain-figma pada repositori", "tiga SVG siap impor ke Figma beserta panduan"],
        ["Aplikasi", "http://127.0.0.1:8000", "demo lokal tanpa akun, jalankan python server.py sesuai README"],
        ["Video demo", "menyusul menjelang Demo Day", "mengikuti skenario uji Bab 8.3"],
    ], lebar=[3.2, 6.2, 6.6], ukuran=9, padat=True)

    pecah_halaman()


# ======================================================================
# DAFTAR ISI (dua lintasan, nomor halaman diisi lintasan kedua)
# ======================================================================
ENTRI_TOI = [
    ("Ringkasan Eksekutif", "ringkasan"),
    ("Bab 1 Pendahuluan", "bab1"),
    ("Bab 2 Analisis Peluang dan Pengguna", "bab2"),
    ("Bab 3 Strategi Data dan Pendekatan AI", "bab3"),
    ("Bab 4 Metrik Keberhasilan dan MVQ", "bab4"),
    ("Bab 5 Spesifikasi Produk (AI PRD)", "bab5"),
    ("Bab 6 Rancangan UX dan Arsitektur Informasi", "bab6"),
    ("Bab 7 Arsitektur dan Implementasi Teknis", "bab7"),
    ("Bab 8 Pengujian dan Evaluasi", "bab8"),
    ("Bab 9 Ekonomi AI", "bab9"),
    ("Bab 10 Governance, Etika, dan Keamanan", "bab10"),
    ("Bab 11 Strategi Adopsi dan Rencana Lanjutan", "bab11"),
    ("Bab 12 Penutup", "bab12"),
    ("Daftar Pustaka", "pustaka"),
    ("Lampiran A sampai E", "lampiran"),
]


def daftar_isi():
    h1("Daftar Isi")
    tabel(None, ["Bagian", "Halaman"],
          [[nama, str(HALAMAN_ISI.get(kunci, "..."))] for nama, kunci in ENTRI_TOI],
          lebar=[13.0, 3.0])
    p("Catatan pembacaan: setiap bab ditutup dengan daftar periksa yang memetakan isi bab kebutir penilaian Demo Day.", ukuran=10.5, miring=True)
    pecah_halaman()


# ======================================================================
# RINGKASAN EKSEKUTIF
# ======================================================================
def ringkasan():
    h1("Ringkasan Eksekutif")
    tabel(None, ["Bagian", "Isi"], [
        ["Masalah", "Petani padi dan jagung di Bogor memberi pupuk dari kebiasaan atau ikut-ikutan tetangga padahal kondisi hara antarpetak berbeda. Uji tanah laboratorium berbayar dan lambat, sedangkan aplikasi peta hara yang ada, termasuk SAFRONS yang kami audit, berhenti pada saran umum tanpa angka dosis."],
        ["Solusi AI", "PupukPintar, aplikasi web mobile-first yang memprediksi dosis pupuk N, P, K (kg/ha) spesifik per lahan dengan model Random Forest, lengkap keyakinan, konversi kebutuhan per petak, estimasi biaya, dan paket sesuai modal."],
        ["Pendekatan AI dan data", "Predictive sebagai inti (Random Forest Regressor, 300 pohon), rule-based sebagai pelindung (rentang aman Permentan 40/2007, kaidah Balittanah, peringatan pengapuran), dan penjelasan berbasis templat. Data latih 6.000 baris proxy hasil ekstraksi logika tabel resmi."],
        ["Hasil uji utama", f"Agreement rekomendasi dalam rentang pakar {str(CV['agreement_persen']).replace('.', ',')} persen (uji silang 5-fold) dan {str(HOLD['agreement_persen']).replace('.', ',')} persen pada data holdout 20 persen, melampaui target MVQ 85 sampai 90 persen. MAE 3,6 kg/ha untuk N, 2,4 untuk P, dan 2,1 untuk K. Latensi API rata-rata 71 milidetik. Seluruh 12 pengujian API dan 20 langkah uji antarmuka lulus."],
        ["Status MVQ", "Tercapai untuk enam dimensi yang dapat diuji tanpa pengguna sasaran (akurasi, waktu respons, guardrail, explainability, cakupan domain, alur singkat). Kepuasan petani belum diukur karena uji lapangan bersama poktan masih direncanakan dan itu kami nyatakan sebagai keterbatasan."],
        ["Biaya operasional", "Sekitar Rp 90.000 per bulan untuk satu server kecil pada skenario pilot (belum memakai LLM sehingga tidak ada biaya token), atau sekitar Rp 240 per prediksi pada skenario pilot dan turun ke sekitar Rp 12 per prediksi pada skenario 500 petani."],
        ["Risiko utama dan mitigasi", "Rekomendasi keliru pada kondisi yang jarang ada di data latih. Mitigasi yang sudah berjalan dan diuji: keluaran dikunci rentang aman resmi, keyakinan rendah atau input di luar sebaran membuat sistem menolak menampilkan angka, dan hasil diarahkan ke verifikasi penyuluh atau uji laboratorium."],
        ["Rencana lanjutan", "Pilot bersama satu poktan di wilayah Bogor pada musim tanam hujan berikutnya, disertai pengumpulan data uji tanah dan panen untuk melatih ulang model."],
    ], lebar=[4.2, 11.8], ukuran=9.5)
    pecah_halaman()


# ======================================================================
# BAB 1 PENDAHULUAN
# ======================================================================
def bab1():
    h1("Bab 1 Pendahuluan")
    p("Bab ini menjelaskan masalah yang diselesaikan PupukPintar, tujuan yang terukur, dan batas pekerjaan kelompok. Problem statement diambil dari LKP-P3 yang sudah direfinasi setelah audit SAFRONS pada LKP-P1.")

    h2("1.1 Latar belakang")
    p("Bogor adalah salah satu wilayah penghasil padi dan jagung di Jawa Barat dengan ratusan ribu petani rumah tangga (BPS, Statistik Indonesia). Pola pemupukan yang kami amati dan yang juga terdokumentasi di publikasi penyuluhan berulang: dosis ditentukan dari kebiasaan turun-temurun atau mengikuti tetangga, bukan dari kondisi lahan sendiri. Padahal dua petak yang bersebelahan bisa punya pH dan stok hara yang berbeda jauh.")
    p("Akibatnya dua hal terjadi. Kelebihan pupuk membuang uang petani dan menumpuk unsur hara yang tidak terpakai, bahkan mencemari air. Kekurangan pupuk membuat hasil panen di bawah potensi. Rekomendasi resmi yang mempertimbangkan kondisi tanah memang tersedia melalui uji tanah laboratorium, tetapi prosesnya berbayar dan berminggu-minggu, sehingga jarang dijangkau petani kecil.")
    p("Kami menemukan celah tersebut lewat audit langsung terhadap SAFRONS, aplikasi peta hara 191 area Bogor buatan mahasiswa IPB, pada LKP-P1. SAFRONS bagus dari sisi data dan tata kelola, tetapi sepenuhnya deterministik dan yang paling kami soroti, aplikasi bernama Fertilizer Recommendation System itu berhenti pada saran umum seperti lakukan pemupukan berimbang tanpa pernah mengeluarkan angka dosis per lahan. PupukPintar dibangun untuk menutup celah itu pada domain, wilayah, dan pengguna yang sama.")

    h2("1.2 Problem statement final")
    p("Petani padi dan jagung kecil dan menengah di Bogor membutuhkan cara cepat, murah, dan mudah untuk mengetahui dosis pupuk N, P, K yang tepat untuk lahannya sendiri karena kondisi hara antarpetak berbeda dan uji tanah laboratorium sulit dijangkau, sehingga saat ini dosis sering salah, biaya membengkak, dan hasil panen tidak optimal.")
    p("Perubahan dari versi awal (audit LKP-P1 ke LKP-P3):")
    tabel("Tabel 1.2 Perubahan problem statement dari versi awal", ["Problem statement awal", "Masukan yang diterima", "Problem statement final"], [
        ["Aplikasi peta hara belum memberi rekomendasi pupuk", "Hasil audit LKP-P1 menunjukkan janji rekomendasi tidak tuntas, dan kuliah tamu menekankan masalah harus tunggal serta terukur", "Fokus dipertajam dari aplikasi peta menjadi satu masalah petani, yaitu angka dosis per lahan yang terjangkau dan cepat"],
        ["Petani sering salah dosis", "Refinasi meminta dampak yang bisa diukur, bukan keluhan umum", "Dampak dirinci menjadi biaya pupuk membengkak dan hasil panen di bawah potensi, dengan target penghematan minimal 10 persen"],
        ["Cakupan produk masih luas (semua komoditas)", "Prinsip satu masalah pada template laporan", "MVP dibatasi padi dan jagung di Bogor dan sekitarnya, sisanya masuk roadmap"],
    ], lebar=[5.0, 5.0, 6.0], ukuran=10)

    h2("1.3 Tujuan")
    tabel("Tabel 1.1 Tujuan produk, indikator, dan target", ["No", "Tujuan produk", "Indikator keberhasilan", "Target"], [
        ["1", "Memberi angka dosis NPK yang sejalan dengan rekomendasi pakar", "Agreement rekomendasi dalam rentang pakar (deviasi maksimal 12,5 persen)", "Minimal 85 sampai 90 persen"],
        ["2", "Mempercepat perhitungan rekomendasi", "Waktu dari tekan Hitung Rekomendasi sampai hasil tampil", "Kurang dari 5 detik"],
        ["3", "Menjaga keamanan keputusan", "Persentase keluaran yang keluar dari rentang aman resmi", "0 persen (guardrail 100 persen)"],
        ["4", "Membuat hasil bisa dipahami petani awam", "Setiap hasil menyertakan penjelasan faktor utama dan tingkat keyakinan", "100 persen hasil"],
        ["5", "Menekan biaya pemupukan", "Rata-rata penghematan biaya pupuk pengguna dibanding praktik sebelumnya", "Minimal 10 persen per musim (diukur saat pilot)"],
    ], lebar=[1.0, 6.0, 5.6, 3.4], ukuran=10)
    p("Tujuan 1 sampai 4 sudah diuji pada Bab 8. Tujuan 5 membutuhkan data lapangan dan statusnya dijelaskan jujur di Bab 12.")

    h2("1.4 Ruang lingkup")
    tabel("Tabel 1.3 Ruang lingkup MVP", ["Dikerjakan di versi MVP", "Sengaja tidak dikerjakan", "Alasan"], [
        ["Input lahan: gambar petak sendiri di peta, pilih unit peta SAFRONS, atau hasil uji tanah", "Diagnosis hama dan penyakit dari foto", "Fitur inti memprediksi dari angka, bukan citra, dan beban pengumpulan data foto besar"],
        ["Prediksi dosis NPK dengan keyakinan dan guardrail", "Draf RDKK otomatis tingkat kelompok", "Butuh akumulasi data banyak petani yang belum ada"],
        ["Konversi kebutuhan pupuk per petak, estimasi biaya, dan paket", "Agen AI yang mengeksekusi otomatis (memesan pupuk, memfinalkan dokumen)", "Keputusan berisiko tinggi tetap pada manusia (prinsip augmented)"],
        ["Penjelasan bahasa sederhana dan peringatan dini", "Peta hara kolaboratif real-time", "Data uji tanah petani baru terkumpul setelah pilot"],
        ["Riwayat rekomendasi dan verifikasi penyuluh (lokal)", "Komoditas dan wilayah di luar padi-jagung dan Bogor", "Data latih proxy baru mencakup dua komoditas tersebut"],
    ], lebar=[6.0, 5.0, 5.0], ukuran=10)

    h2("1.5 Sistematika laporan")
    p("Bab 2 menjelaskan peluang dan pengguna. Bab 3 menjelaskan strategi data dan pendekatan AI. Bab 4 menetapkan metrik dan MVQ. Bab 5 merangkum spesifikasi produk. Bab 6 menjelaskan rancangan UX dan penanganan ketidakpastian. Bab 7 mendokumentasikan implementasi teknis. Bab 8 menyajikan pengujian dan evaluasi. Bab 9 menghitung ekonomi AI. Bab 10 membahas governance dan keamanan. Bab 11 menyusun strategi adopsi. Bab 12 menutup dengan kesimpulan, keterbatasan, dan kontribusi anggota.")

    daftar_periksa([
        ["Latar belakang memuat angka dan sumber", "Terpenuhi (biaya lab sebagai asumsi yang ditandai, celah SAFRONS dari audit LKP-P1)"],
        ["Problem statement hanya satu masalah dan memakai pola yang dianjurkan", "Terpenuhi (pola pengguna, kebutuhan, kendala, dampak)"],
        ["Perubahan dari versi awal ditunjukkan", "Terpenuhi (Tabel 1.2)"],
        ["Setiap tujuan punya indikator dan target", "Terpenuhi (Tabel 1.1)"],
        ["Ada daftar hal yang sengaja tidak dikerjakan", "Terpenuhi (Tabel 1.3)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 2 ANALISIS PELUANG DAN PENGGUNA
# ======================================================================
def bab2():
    h1("Bab 2 Analisis Peluang dan Pengguna")

    h2("2.1 Benchmarking produk eksisting")
    tabel("Tabel 2.1 Pembanding produk dan celah yang kami isi", ["Produk atau jalur", "Pembuat atau asal", "Fitur utama", "Pendekatan AI", "Kelemahan", "Celah yang kami isi"], [
        ["SAFRONS (produk yang kami audit)", "Tim CAPS-32 Ilmu Komputer IPB", "Peta hara 191 area Bogor, diagnosis kaidah Balittanah, simulasi kesesuaian komoditas", "Rule-based murni (deterministik)", "Tidak ada angka dosis, tidak ada tingkat keyakinan, tidak belajar dari data baru", "Dosis NPK per lahan dengan keyakinan dan guardrail"],
        ["Ask RANI", "Elevarm (materi kuliah tamu)", "Asisten tanya jawab pertanian", "Generative (chatbot)", "Fokus pada jawaban atas pertanyaan, bukan perhitungan dosis spesifik lahan", "Angka dosis terukur yang dikunci rentang resmi"],
        ["Uji tanah laboratorium", "Balai pengujian tanah", "Analisis pH, N, P, K, tekstur", "Tidak ada (analisis lab)", "Berbayar, lambat, jangkauan terbatas untuk petani kecil", "Perkiraan dosis instan tanpa biaya lab, dengan jalur rujukan ke lab saat ragu"],
    ], lebar=[3.0, 2.6, 3.2, 2.2, 3.0, 3.4], ukuran=9.5)
    p("Tiga pembanding ini menunjukkan ruang yang belum diisi, yaitu angka dosis spesifik lahan yang cepat, gratis bagi petani, dan tetap aman karena dikunci rentang resmi.")

    h2("2.2 Posisi pada AI Opportunity Tree")
    tabel("Tabel 2.2 Posisi produk pada empat cabang AI Opportunity Tree (LKP-P2)", ["Cabang", "Dipakai?", "Bentuknya di produk kami"], [
        ["Automation", "Sebagian (ditunda)", "Riwayat rekomendasi tersimpan otomatis per petak, sedangkan draf RDKK otomatis ditunda ke versi lanjutan"],
        ["Augmentation", "Ya (cabang utama)", "AI menyusun angka dosis, petani meninjau, penyuluh memverifikasi sebelum dijalankan"],
        ["Personalization", "Sebagian", "Rekomendasi memakai kondisi lahan dan target hasil masing-masing petani, ditambah paket sesuai modal"],
        ["Inspiration", "Tidak (versi ini)", "Simulasi skenario dan peta kolaboratif dicatat sebagai ide lanjutan"],
    ], lebar=[3.0, 3.0, 10.0], ukuran=10)
    p("Cabang utama kami Augmentation karena keputusan pemupukan berdampak langsung ke uang dan tanaman, sehingga AI paling tepat berperan sebagai penyusun rekomendasi yang tetap diverifikasi manusia.")

    h2("2.3 Matriks prioritisasi peluang")
    tabel("Tabel 2.3 Matriks prioritisasi delapan ide fitur (skala 1 sampai 5, dari LKP-P2)", ["Alternatif ide", "Business Value", "User Feasibility", "Data Availability", "Risk Level", "Total", "Keputusan"], [
        ["G1. Rekomendasi dosis pupuk berbasis ML", "5", "5", "5", "4", "19", "Dipilih (fokus)"],
        ["A1. Riwayat hara lahan otomatis", "3", "5", "5", "5", "18", "Cadangan"],
        ["A2. Draf RDKK otomatis", "4", "4", "4", "5", "17", "Ditunda"],
        ["P1. Paket pemupukan sesuai modal", "4", "4", "4", "4", "16", "Ditunda, sebagian diambil sebagai fitur hasil"],
        ["G2. Peringatan risiko pengelolaan lahan", "4", "4", "3", "4", "15", "Ditunda, sebagian diambil sebagai peringatan rule-based"],
        ["P2. Kalender pemupukan pribadi", "3", "4", "3", "5", "15", "Ditunda"],
        ["I1. Simulasi skenario pemupukan", "4", "4", "3", "3", "14", "Ditunda"],
        ["I2. Peta hara kolaboratif", "4", "3", "3", "4", "14", "Ditunda"],
    ], lebar=[5.2, 1.7, 1.9, 1.9, 1.6, 1.2, 2.5], ukuran=9)
    p("Ide G1 menang karena menjawab langsung celah terbesar SAFRONS, yaitu janji rekomendasi tanpa angka. Skor risikonya 4, bukan 5, karena dosis salah berdampak nyata, sehingga sejak awal kami menetapkan guardrail rentang aman, tingkat keyakinan, dan jalur verifikasi penyuluh. Dua ide yang ditunda sebagian isinya justru terealis sebagai fitur pendukung hasil (paket modal dan peringatan dini).")

    h2("2.4 Persona dan skenario pengguna")
    tabel("Tabel 2.4 Persona utama (kandidat, belum divalidasi wawancara lapangan)", ["Aspek", "Isi"], [
        ["Nama (samaran) dan peran", "Pak Wandi, petani padi dan jagung, anggota poktan"],
        ["Usia, lokasi, pengalaman", "41 tahun, desa di Kecamatan Cibinong, menggarap lahan 0,5 sampai 1 hektar sejak 15 tahun lalu"],
        ["Literasi digital dan perangkat", "Smartphone Android jadul, kuota terbatas, sinyal memadai di rumah dan kios saprodi, terbiasa WhatsApp"],
        ["Tujuan", "Menekan biaya pupuk tanpa menurunkan hasil, karena harga pupuk adalah komponen biaya budidaya yang paling terasa"],
        ["Kendala saat ini", "Dosis mengikuti kebiasaan tetangga, uji tanah lab dianggap mahal dan ribet, rekomendasi penyuluh tunggu giliran kunjungan"],
        ["Sumber data persona", "Profil pengguna awal dari LKP-P2 dan LKP-P3 (petani muda poktan pengguna smartphone) serta pengamatan audit LKP-P1. Belum ada wawancara lapangan, sehingga persona ini kandidat yang akan divalidasi saat pilot. Kejujuran ini kami catat juga di daftar periksa bab"],
    ], lebar=[4.2, 11.8], ukuran=10)
    tabel("Tabel 2.5 Skenario tanpa dan dengan produk", ["Skenario", "Tanpa produk (kondisi sekarang)", "Dengan produk"], [
        ["Menyusun kebutuhan pupuk musim tanam", "Meniru dosis tetangga, kadang sisa pupuk menumpuk atau kurang", "Input lahan dan target hasil, mendapat dosis kg/ha plus kebutuhan pupuk per petak dalam hitungan detik"],
        ["Menyusun anggaran beli pupuk", "Membeli berdasarkan perkiraan, sering kehabisan atau kelebihan", "Estimasi biaya langsung dari kebutuhan per petak dengan pilihan paket hemat, standar, atau optimal"],
        ["Menghadapi kondisi lahan aneh", "Memupuk seperti biasa meski tanah sangat masam", "Sistem menolak memaksakan angka, memberi peringatan pengapuran, dan mengarahkan ke uji lab atau penyuluh"],
    ], lebar=[3.6, 6.2, 6.2], ukuran=10)

    h2("2.5 Value proposition dan Lean Canvas")
    tabel("Tabel 2.6 Ringkasan AI Lean Canvas (pengembangan dari LKP-P2)", ["Elemen", "Isi"], [
        ["Value proposition", "Dosis pupuk yang tepat untuk lahan Anda, bukan untuk lahan orang lain, lengkap dengan biayanya"],
        ["Problem", "Dosis dari kebiasaan, uji lab sulit dijangkau, dan aplikasi yang ada berhenti di saran umum"],
        ["Customer segments", "Petani padi dan jagung 0,25 sampai 2 ha di Bogor, penyuluh sebagai verifikator, pengurus poktan penyusun RDKK"],
        ["Solution", "Prediksi dosis NPK per lahan dengan keyakinan, konversi per petak, estimasi biaya, paket sesuai modal"],
        ["Channels", "Penyuluh dan poktan, sosialisasi di kios saprodi, tautan aplikasi dari grup poktan"],
        ["Revenue streams", "Gratis bagi petani pada tahap pilot, iuran layanan poktan direncanakan setelah fitur rekap RDKK jalan (Bab 9.5)"],
        ["Cost structure", "Hosting server kecil dan pelatihan ulang model tiap musim, tanpa biaya token karena tidak memakai LLM"],
        ["Key metrics", "Agreement dengan pakar, penghematan biaya petani, retensi antarmusim, persentase rekomendasi terverifikasi penyuluh"],
        ["Unfair advantage", "Keselarasan dengan peta hara SAFRONS dan jaringan poktan di Bogor, plus guardrail kepatuhan tabel resmi yang sulit ditiru aplikasi generik"],
    ], lebar=[4.2, 11.8], ukuran=10)

    daftar_periksa([
        ["Minimal tiga produk pembanding dengan celah yang jelas", "Terpenuhi (Tabel 2.1)"],
        ["Ide terpilih tampak di matriks prioritisasi lengkap dengan alasan", "Terpenuhi (Tabel 2.3)"],
        ["Persona berdasarkan data dari pengguna nyata dengan sumbernya", "Sebagian, persona kandidat dari LKP dan pengamatan audit, wawancara lapangan dijadwalkan saat pilot (jujur kami nyatakan)"],
        ["Lean Canvas selaras dengan Bab 4 dan Bab 9", "Terpenuhi"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 3 STRATEGI DATA DAN PENDEKATAN AI
# ======================================================================
def bab3():
    h1("Bab 3 Strategi Data dan Pendekatan AI")

    h2("3.1 Peta modalitas data")
    tabel("Tabel 3.1 Modalitas data yang benar-benar dipakai produk", ["Modalitas", "Contoh data spesifik", "Berlabel?", "Sumber", "Jumlah", "Preprocessing"], [
        ["Tabular", "pH, N, P, K, tekstur, komoditas, target hasil, musim, label dosis N-P-K", "Ya", "Ekstraksi logika tabel Permentan 40/2007 dan kelas Balittanah (skrip data_proxy.py)", "6.000 baris", "Pembulatan, one-hot encoding kategorikal, rentang dicek ulang terhadap tabel resmi"],
        ["Spasial", "Peta hara 191 area wilayah Bogor untuk input cepat (pH rata-rata dan band N-P-K)", "Tidak dipakai melatih", "Data spasial asli SAFRONS dari kode yang kami audit (hara-bogor.geojson, diproses gen_peta.py)", "191 area, 3 di antaranya tanpa data", "Konversi proyeksi UTM ke WGS84, penyederhanaan geometri, pemetaan band N-P-K ke nilai perwakilan skala model (Lampiran C)"],
        ["Teks", "Publikasi teknis rekomendasi pemupukan sebagai rujukan guardrail dan materi tips penyuluhan", "Tidak dipakai melatih", "Dokumen Permentan dan publikasi Balittanah", "Dokumen rujukan", "Diterjemahkan menjadi batas kelas dan kalimat peringatan"],
    ], lebar=[2.0, 4.0, 1.7, 4.2, 1.6, 2.5], ukuran=9)
    p("Jumlah data yang kami tulis adalah jumlah nyata yang kami miliki sekarang, bukan yang direncanakan. Data uji tanah petani belum ada dan statusnya jujur dicatat sebagai kebutuhan pilot.")

    h2("3.2 Pendekatan AI yang dipilih")
    tabel("Tabel 3.2 Pendekatan AI dan perannya", ["Tipe AI", "Dipakai?", "Use case di produk", "Keunggulan", "Trade-off atau tantangan"], [
        ["Predictive", "Ya", "Random Forest Regressor memprediksi dosis N, P, K (kg/ha) dan menyediakan keyakinan dari sebaran antarpohon", "Menangkap hubungan tidak linear, punya feature importance untuk penjelasan", "Keyakinan antarpohon adalah perkiraan, bukan jaminan statistik (dianalisis di Bab 8.4)"],
        ["Rule-based", "Ya", "Kelas status hara kaidah Balittanah, peringatan pengapuran, penahanan keluaran pada rentang Permentan, penolakan input buruk", "Deterministik, mudah diuji, patuh tabel resmi", "Aturan statis, harus diperbarui bila tabel resmi berubah"],
        ["Generative", "Diubah pada implementasi", "Rencana awal LKP-P3 memakai model bahasa untuk penjelasan, implementasi final memakai templat rule-based", "Tanpa biaya token, tanpa risiko halusinasi angka, latensi nol", "Penjelasan lebih kaku, namun akurat dan selalu sesuai data model"],
        ["Agentic", "Tidak", "Tidak ada tindakan otomatis pada versi ini", "Risiko tetap di tangan manusia", "Bukan trade-off, pilihan sadar sesuai toleransi kesalahan produk"],
    ], lebar=[2.2, 1.8, 4.6, 3.6, 3.8], ukuran=9)
    p("Perubahan penjelasan dari generative ke templat rule-based adalah keputusan implementasi yang penting. Selain meniadakan risiko model bahasa mengarang angka, biaya operasional produk menjadi hampir nol (Bab 9) dan waktu respons tetap di bawah 100 milidetik. Keputusan ini dicatat juga di Bab 5.1 sebagai perubahan sejak PRD v1.0.")

    h2("3.3 Akuisisi, pembersihan, dan pelabelan data")
    tabel("Tabel 3.3 Strategi data", ["Aspek", "Isi"], [
        ["Akuisisi data", "Cold start ditangani sesuai strategi LKP-P4: dataset proxy dibangun dari logika tabel resmi Permentan 40/2007 (rentang dosis padi dan jagung) dan kelas interpretasi kesuburan Balittanah, bukan dataset publik pihak ketiga yang tidak punya label dosis. Data uji tanah petani direncanakan dikumpulkan bertahap bersama poktan"],
        ["Pembersihan data", "Label dosis langsung dikunci pada rentang aman resmi pada saat pembangkitan, sehingga tidak ada baris di luar rentang. Nilai fitur dibangkitkan pada rentang wajar (pH 3,8 sampai 8,2, dst), input di luar itu ditolak validasi di aplikasi"],
        ["Strategi pelabelan", "Semi-automated sesuai LKP-P4: fungsi dosis_ahli mengekstraksi logika tabel menjadi label, kemudian logikanya diperiksa ulang manual oleh tim terhadap dokumen resmi. Panduan pelabelan ada di Lampiran C"],
        ["Penjaminan mutu label", "Fungsi label deterministik sehingga konsisten antarpenilai. Rentang label diaudit otomatis (guardrail sama dengan produk). Kaidah pembacaan tabel didokumentasikan dan dapat diperiksa di skrip"],
        ["Data tidak seimbang", "Kondisi ekstrem lebih jarang pada label karena koreksi proporsional. Mitigasi pada produk: input di luar sebaran data latih ditandai dan tidak dipaksakan prediksi, serta rencana pengumpulan data ekstrem saat pilot"],
        ["Bias data dan mitigasi", "Sampling bias (wilayah proxy mengikuti rentang Bogor, di luar itu diberi peringatan), label bias (label mengikuti tabel resmi yang menyasar target hasil tertentu, disampaikan di penjelasan bahwa target hasil ikut memengaruhi dosis), feature bias (faktor modal tidak masuk model, dijembatani paket hemat-standar-optimal)"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("3.4 Data pipeline dan feature engineering")
    gambar(os.path.join(GAMBAR, "gambar", "pipeline_data.png"), "Gambar 3.1 Pipeline data dari tabel resmi sampai model siap sajikan", 15.5)
    tabel("Tabel 3.4 Fitur terpenting model dan alasannya", ["Fitur", "Data mentah asal", "Transformasi", "Mengapa penting"], [
        ["pH tanah", "Input uji tanah atau peta hara SAFRONS", "Nilai numerik langsung", "Menentukan ketersediaan hara, pH di bawah 5,5 menaikkan kebutuhan P sebelum pengapuran"],
        ["N (%)", "Input uji tanah atau peta hara SAFRONS", "Nilai numerik langsung", "Stok nitrogen awal mengurangi dosis N yang perlu diberikan"],
        ["P (ppm)", "Input uji tanah atau peta hara SAFRONS", "Nilai numerik langsung", "Stok fosfat, sering menjadi faktor pembatas pada tanah masam"],
        ["K (me/100g)", "Input uji tanah atau peta hara SAFRONS", "Nilai numerik langsung", "Stok kalium berkaitan dengan kualitas butir dan ketahanan tanaman"],
        ["Tekstur tanah", "Input pilihan pengguna", "One-hot encoding (3 kelas)", "Tanah liat menyimpan hara lebih baik sehingga sedikit lebih hemat dosis"],
        ["Komoditas dan target hasil", "Pilihan dan input pengguna", "One-hot encoding dan numerik", "Padi dan jagung punya kebutuhan dasar berbeda, target hasil menaikkan kebutuhan"],
        ["Musim tanam", "Pilihan pengguna (bawaan dari kalender)", "One-hot encoding (2 kelas)", "Musim hujan menaikkan risiko pencucian N sehingga dosis N sedikit lebih tinggi"],
    ], lebar=[2.8, 3.8, 3.4, 6.0], ukuran=9.5)
    gambar(os.path.join(GAMBAR, "gambar", "feature_importance.png"), "Gambar 3.2 Feature importance Random Forest pada data latih", 13.0)
    p("Feature importance menunjukkan komoditas, target hasil, dan stok hara sebagai penentu utama, konsisten dengan logika tabel resmi. Artinya model belajar sejalan dengan kaidah pakar, bukan melawannya.")

    h2("3.5 Pemilihan algoritma atau model")
    tabel("Tabel 3.5 Kandidat model dan hasil uji singkat", ["Kandidat model", "Kelebihan", "Kekurangan", "Hasil uji singkat (holdout 20 persen)"], [
        ["Baseline rata-rata per komoditas", "Sangat sederhana, sebagai pembanding minimum", "Mengabaikan kondisi lahan", "Agreement 49,2 persen, MAE N 24,0 kg/ha"],
        ["Regresi linear", "Mudah dijelaskan", "Tidak menangkap hubungan tidak linear", "Agreement 89,5 persen, MAE N 11,6 kg/ha"],
        ["Random Forest Regressor (terpilih)", "Menangkap non-linear, tahan noise, punya feature importance, mudah diekspor joblib", "Ukuran model lebih besar, keyakinan dari antarpohon bersifat perkiraan", "Agreement 95,2 persen, MAE N 3,6 kg/ha"],
        ["Gradient Boosting", "Sering akurat lebih tinggi", "Lebih sensitif overfit pada data proxy, set feature importance lebih rumit dijelaskan", "Tidak dipilih, menunggu data lapangan lebih beragam"],
    ], lebar=[3.6, 4.0, 4.0, 4.4], ukuran=9.5)
    p("Model terpilih Random Forest dengan n_estimators=300 dan min_samples_leaf=3 karena paling sesuai dengan data dan masalah kami, bukan karena paling canggih. Pertimbangannya akurasi yang melampaui target, latensi di bawah 100 milidetik tanpa GPU, keluaran yang tetap bisa dijelaskan lewat feature importance, dan kemudahan pelatihan ulang tiap musim.")

    daftar_periksa([
        ["Setiap sumber data punya nama, tautan, dan lisensi", "Terpenuhi, tabel retensi dan skrip pembangkit data ada di Lampiran C"],
        ["Jumlah data yang ditulis adalah jumlah nyata", "Terpenuhi (6.000 baris proxy, 191 area peta SAFRONS)"],
        ["Pendekatan AI dipilih dengan alasan dan trade-off", "Terpenuhi (Tabel 3.2, 3.5)"],
        ["Strategi pelabelan beserta penjaminan mutunya dijelaskan", "Terpenuhi, panduan di Lampiran C"],
        ["Bias data diidentifikasi beserta mitigasinya", "Terpenuhi (Tabel 3.3)"],
        ["Alasan pemilihan model dijelaskan", "Terpenuhi (Tabel 3.5)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 4 METRIK DAN MVQ
# ======================================================================
def bab4():
    h1("Bab 4 Metrik Keberhasilan dan MVQ")

    h2("4.1 Pemetaan metrik ML ke metrik produk")
    tabel("Tabel 4.1 Pemetaan metrik ML ke metrik produk", ["Metrik ML", "Metrik produk", "Bagaimana hubungannya", "Target"], [
        ["Agreement rekomendasi dalam rentang pakar (deviasi maksimal 12,5 persen)", "Penerimaan rekomendasi oleh penyuluh dan petani, penghematan biaya pupuk", "Makin banyak prediksi masuk rentang pakar, makin sedikit koreksi penyuluh dan makin besar kemungkinan rekomendasi dijalankan", "Agreement 85 sampai 90 persen, penghematan minimal 10 persen per musim"],
        ["MAE per unsur hara (kg/ha)", "Selisih beli pupuk dari kebutuhan ideal", "Galat kecil berarti kebutuhan per petak yang dicetak aplikasi mendekati kebutuhan sebenarnya", "MAE di bawah 10 persen dosis rata-rata per unsur"],
        ["Kalibrasi tingkat keyakinan", "Kepercayaan pengguna dan retensi antarmusim", "Sistem yang menolak menebak pada kasus meragukan menjaga petani dari angka keliru, sehingga petani mau kembali", "Retensi minimal 60 persen (diukur saat pilot)"],
        ["Latensi prediksi", "Kenyamanan pemakaian", "Hasil yang muncul sekejap membuat alur tiga ketukan terasa utuh", "Kurang dari 5 detik"],
    ], lebar=[4.2, 3.6, 5.2, 3.0], ukuran=9.5)

    h2("4.2 Dampak kesalahan model")
    tabel("Tabel 4.2 Dampak false positive dan false negative", ["Jenis kesalahan", "Contoh kejadian di produk", "Dampak bagi pengguna", "Metrik yang diprioritaskan"], [
        ["False positive (rekomendasi salah tetapi tampil meyakinkan)", "Model memberi dosis N jauh berlebih pada tanah yang sebenarnya subur, tampil dengan tampilan percaya diri", "Uang petani terbakar, tanah dan air terbebani hara, kepercayaan hilang sekali pakai", "Precision pada kepatuhan rentang aman, guardrail kunci keluaran"],
        ["False negative (kasus penting terlewat)", "Tanah sangat masam tidak diberi peringatan pengapuran sehingga pupuk P sia-sia", "Pemupukan tidak efektif, biaya tetap keluar", "Cakupan aturan Balittanah, uji guardrail peringatan"],
    ], lebar=[3.8, 5.4, 3.8, 3.0], ukuran=9.5)
    p("Keputusan trade-off: kami mendahulukan jangan menampilkan angka yang salah daripada selalu menampilkan angka. Karena itu sistem berani tidak yakin, yaitu menyembunyikan angka pada keyakinan rendah atau input di luar sebaran dan mengarahkan ke uji lab atau penyuluh. Jalur ini menjaga kasus yang tidak tertangkap model tetap punya tempat kembali.")

    h2("4.3 Hasil model baseline")
    tabel("Tabel 4.3 Perbandingan model utama dengan baseline pada data holdout (1.200 baris, tidak dipakai melatih)", ["Model", "Metrik", "Nilai", "Catatan"], [
        ["Baseline rata-rata per komoditas", "Agreement, MAE N", "49,2 persen, 24,0 kg/ha", "Mengabaikan kondisi lahan, jelas tidak layak"],
        ["Baseline regresi linear", "Agreement, MAE N", "89,5 persen, 11,6 kg/ha", "Lumayan, tetapi MAE N dua kali lipat model utama"],
        ["Model utama Random Forest", "Agreement, MAE N, P, K", "95,2 persen, 3,6, 2,4, 2,1 kg/ha", "Melampaui target MVQ dan kedua baseline"],
    ], lebar=[4.6, 3.2, 4.4, 3.8], ukuran=10)
    p("Metrik dihitung pada pembagian data yang sama (seed 7) sehingga perbandingannya adil. Skrip penghitungannya ada di tests/evaluasi_tambahan.py dan dapat diulang siapa pun.")

    h2("4.4 Minimum Viable Quality (MVQ)")
    tabel("Tabel 4.4 Ambang MVQ yang ditetapkan sebelum pengujian Bab 8", ["Dimensi kualitas", "Ambang MVQ", "Hasil saat ini", "Lolos?"], [
        ["Ketepatan keluaran AI", "Agreement minimal 85 sampai 90 persen", f"95,2 persen pada holdout (CV 5-fold {str(CV['agreement_persen']).replace('.', ',')} persen)", "Ya"],
        ["Waktu respons", "Kurang dari 5 detik per rekomendasi", "p95 API 87 milidetik, model 63,8 milidetik", "Ya"],
        ["Keamanan keluaran", "0 keluaran di luar rentang aman resmi", "12 dari 12 pengujian guardrail lulus, termasuk 45 kombinasi input ekstrem padi", "Ya"],
        ["Cakupan domain", "Padi dan jagung pada rentang data latih", "Dua komoditas terpasang, input di luar domain ditolak dengan pesan jelas", "Ya"],
        ["Explainability", "100 persen hasil menyertakan penjelasan dan keyakinan", "Seluruh jawaban API memuat field penjelasan dan keyakinan (uji kontrak)", "Ya"],
        ["Keamanan keputusan berisiko tinggi", "100 persen kasus ragu diarahkan ke penyuluh atau uji lab", "Uji luar sebaran dan keyakinan rendah menunjukkan angka disembunyikan", "Ya"],
        ["Kepuasan pengguna petani", "Skor minimal 4 dari 5", "Belum diukur, menunggu pilot poktan", "Belum"],
    ], lebar=[3.6, 4.0, 5.4, 2.0], ukuran=9.5)
    tabel(None, ["Ambang risiko", "Kondisi yang tidak boleh dijawab otomatis"], [
        ["Aturan ambang", "Keyakinan di bawah 0,70, input di luar sebaran data latih, pH di luar 3 sampai 9, target hasil di luar rentang komoditas. Pada kondisi tersebut sistem tidak menampilkan angka dan mengarahkan ke uji laboratorium atau penyuluh"],
    ], lebar=[3.2, 12.8], ukuran=10)

    daftar_periksa([
        ["Setiap metrik ML dihubungkan dengan metrik produk", "Terpenuhi (Tabel 4.1)"],
        ["Dampak FP dan FN dijelaskan dalam konteks pengguna", "Terpenuhi (Tabel 4.2)"],
        ["Ada hasil model baseline sebagai pembanding", "Terpenuhi (Tabel 4.3)"],
        ["MVQ punya ambang terukur ditetapkan sebelum pengujian", "Terpenuhi (Tabel 4.4, ditetapkan dari NFR LKP-P5 sebelum Bab 8 dikerjakan)"],
        ["Ambang risiko untuk keputusan berbahaya ditulis", "Terpenuhi"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 5 SPESIFIKASI PRODUK
# ======================================================================
def bab5():
    h1("Bab 5 Spesifikasi Produk (AI PRD)")

    h2("5.1 Ruang lingkup MVP")
    tabel(None, ["Bagian", "Isi"], [
        ["Ringkasan produk", "PupukPintar adalah aplikasi web mobile-first untuk petani padi dan jagung di Bogor dan sekitarnya yang mengubah kondisi lahan menjadi angka dosis pupuk N, P, K per petak lengkap dengan biayanya"],
        ["In-scope", "Registrasi lahan (peta hara SAFRONS atau uji tanah), prediksi dosis dengan keyakinan dan guardrail, konversi per petak dan biaya, paket modal, penjelasan sederhana, peringatan dini, riwayat, verifikasi penyuluh, consent dan penghapusan data"],
        ["Out-of-scope", "Diagnosis foto, RDKK otomatis, agen eksekusi otomatis, peta kolaboratif real-time, komoditas dan wilayah baru (Bab 1.4)"],
        ["Asumsi", "Petani punya smartphone dan koneksi minimal di rumah, poktan, atau kios saprodi, harga pupuk rujukan relatif stabil dalam satu musim"],
        ["Batasan", "Data latih proxy dari tabel resmi, komoditas terbatas, demo berjalan lokal, waktu satu semester"],
    ], lebar=[3.2, 12.8], ukuran=10)
    p("Perubahan sejak AI PRD v1.0 (UTS) dan alasannya:")
    tabel("Tabel 5.1 Perubahan spesifikasi sejak versi UTS", ["Bagian PRD", "Isi di v1.0 (UTS)", "Isi di versi final", "Alasan berubah"], [
        ["Penjelasan rekomendasi", "Model bahasa generatif menyusun penjelasan", "Templat rule-based menyusun penjelasan dari status hara", "Meniadakan risiko angka dikarang, biaya nol, latensi nol, tetap akurat terhadap data model"],
        ["Sumber input peta", "Peta 191 area SAFRONS", "Alat gambar petak: petani melukis batas petaknya di peta, luas terukur otomatis dari geometri, nilai hara dari unit SAFRONS tempat pusat petak berada; unit lanskap tetap bisa dipilih langsung", "Unit lanskap SAFRONS berbentuk besar sehingga tidak mewakili petak petani, gambaran sendiri membuat bentuk dan luas lahan persis"],
        ["Server API", "FastAPI sesuai LKP-P6", "Server pustaka standar Python dengan kontrak JSON sama", "Ekstensi biner pydantic-core diblokir kebijakan Application Control pada mesin anggota, kontrak tidak berubah sehingga migrasi ke FastAPI mudah (Bab 7.6)"],
        ["Estimasi biaya", "Harga pupuk rujukan umum", "Harga HET Urea Rp 2.250 dan SP-36 Rp 2.300 per kg, KCl pasar Rp 5.000 per kg (asumsi tim)", "Kalkulasi biaya jadi bisa ditelusuri dan diuji konsistensinya"],
    ], lebar=[2.8, 4.0, 4.6, 4.6], ukuran=9)

    h2("5.2 Functional requirements")
    tabel("Tabel 5.2 Daftar fitur dengan user story, prioritas MoSCoW, dan status", ["ID", "Fitur", "User story", "MoSCoW", "AI atau non-AI", "Status"], [
        ["F-01", "Onboarding dan persetujuan data", "Sebagai petani, saya ingin memberi persetujuan data sejak awal, agar saya tahu data saya dipakai untuk apa dan bisa berhenti kapan saja", "Must", "Non-AI", "Selesai"],
        ["F-02", "Daftar lahan: gambar petak di peta, pilih unit, atau uji tanah", "Sebagai petani, saya ingin menggambar batas petak saya di peta sehingga luas dan bentuknya persis, atau memakai unit peta dan hasil uji tanah, agar kondisi hara lahan saya dikenali tanpa lab", "Must", "Non-AI (data spasial)", "Selesai"],
        ["F-03", "Rekomendasi dosis NPK dengan keyakinan", "Sebagai petani, saya ingin menerima angka dosis N, P, K spesifik lahan saya beserta tingkat keyakinan, agar saya tidak lagi menebak takaran", "Must", "AI (predictive + guardrail)", "Selesai"],
        ["F-04", "Konversi per petak, estimasi biaya, paket modal", "Sebagai petani, saya ingin tahu berapa kg pupuk yang harus dibeli dan biayanya, dengan pilihan paket sesuai modal, agar rekomendasi langsung bisa dijalankan", "Must", "Non-AI (kalkulasi deterministik)", "Selesai"],
        ["F-05", "Penjelasan bahasa sederhana", "Sebagai petani awam agronomi, saya ingin tahu alasan rekomendasinya, agar saya paham sebelum menjalankannya", "Should", "AI (templat rule-based)", "Selesai"],
        ["F-06", "Peringatan dini kondisi lahan", "Sebagai petani, saya ingin diperingatkan bila pemupukan tidak efektif, misal tanah masam perlu diapur, agar biaya tidak sia-sia", "Should", "AI (rule-based)", "Selesai"],
        ["F-07", "Riwayat rekomendasi per petak", "Sebagai petani, saya ingin riwayat tersimpan otomatis, agar saya bisa membandingkan antarmusim", "Should", "Non-AI", "Selesai"],
        ["F-08", "Verifikasi penyuluh", "Sebagai penyuluh, saya ingin meninjau dan menyetujui atau meminta koreksi rekomendasi, agar keputusan tetap aman", "Should", "Non-AI", "Selesai (mode demo lokal)"],
        ["F-09", "Draf RDKK kelompok", "Sebagai pengurus poktan, saya ingin rekap kebutuhan anggota jadi draf RDKK", "Could", "Non-AI", "Belum (roadmap Bab 11.4)"],
    ], lebar=[1.0, 3.0, 6.2, 1.3, 2.3, 2.2], ukuran=9)

    h2("5.3 Non-functional requirements")
    tabel("Tabel 5.3 NFR terukur dengan cara mengukur dan hasil", ["Aspek", "Persyaratan terukur", "Cara mengukur", "Hasil"], [
        ["Akurasi model", "Agreement 85 sampai 90 persen dalam rentang pakar", "Uji silang 5-fold dan holdout 20 persen", "94,7 dan 95,2 persen, lulus"],
        ["Waktu respons", "Rekomendasi kurang dari 5 detik", "Pengukuran 30 permintaan API dan uji latensi pytest", "p95 87 milidetik, lulus"],
        ["Privasi data", "Consent onboarding, opsi tolak pelatihan model, hapus data", "Pemeriksaan layar Profil dan uji perjalanan", "Terpasang (F-01), data lokal perangkat"],
        ["Explainability", "Setiap hasil memuat alasan dan keyakinan", "Pemeriksaan kontrak API dan layar hasil", "Terpenuhi pada seluruh jawaban"],
        ["Usability", "Alur beranda sampai hasil maksimal 5 ketukan", "Uji perjalanan UI terotomasi", "3 ketukan, lulus"],
        ["Ketersediaan", "Pesan jelas saat server tidak terjangkau, tidak ada hasil tanpa peringatan", "Simulasi galat jaringan pada penanganan fetch", "Pesan dan tombol coba lagi tersedia"],
    ], lebar=[2.6, 4.8, 4.4, 4.2], ukuran=9.5)

    h2("5.4 Tabel penelusuran fitur")
    tabel("Tabel 5.4 Penelusuran fitur ke desain, komponen teknis, dan skenario uji", ["ID fitur", "Layar (Bab 6)", "Komponen teknis (Bab 7)", "Skenario uji (Bab 8)"], [
        ["F-01", "Splash dan onboarding", "Halaman splash dengan kotak centang consent, state localStorage", "S-01"],
        ["F-02", "Lahan Saya, tambah lahan, peta hara, uji tanah", "GET /api/peta, kanvas peta vektor SVG mandiri dengan alat gambar petak (luas geodesik otomatis) dan pilih unit SAFRONS, formulir uji tanah dengan validasi", "S-02, S-03"],
        ["F-03", "Rekomendasi (formulir dan hasil)", "POST /rekomendasi, mesin model.py, guardrail konstanta.py", "S-04, S-05"],
        ["F-04", "Hasil (kebutuhan, biaya, paket)", "Konversi kadar unsur Urea 46 persen, SP-36 30 persen, KCl 60 persen, harga di konstanta.py", "S-04"],
        ["F-05", "Hasil (penjelasan sederhana)", "Templat penjelasan dari status hara di model.py", "S-04"],
        ["F-06", "Hasil (pita peringatan)", "Aturan pH dan musim di model.py", "S-06"],
        ["F-07", "Riwayat", "Penyimpanan localStorage, halaman riwayat", "S-04"],
        ["F-08", "Papan Penyuluhan (verifikasi)", "Panel verifikasi localStorage dengan aksi setujui atau koreksi", "S-07"],
    ], lebar=[1.4, 4.6, 6.2, 3.8], ukuran=9.5)
    p("PRD final lengkap dengan catatan perubahan tersaji sebagai Lampiran A.")

    daftar_periksa([
        ["Setiap fitur punya ID, user story, prioritas, penanda AI", "Terpenuhi (Tabel 5.2)"],
        ["NFR terukur dengan cara pengukuran", "Terpenuhi (Tabel 5.3)"],
        ["Perubahan sejak AI PRD v1.0 dijelaskan", "Terpenuhi (Tabel 5.1)"],
        ["Tabel penelusuran lengkap untuk fitur Must", "Terpenuhi (Tabel 5.4)"],
        ["AI PRD final terlampir", "Terpenuhi (Lampiran A)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 6 UX
# ======================================================================
def bab6():
    h1("Bab 6 Rancangan UX dan Arsitektur Informasi")

    h2("6.1 Information architecture dan sitemap")
    gambar(os.path.join(GAMBAR, "gambar", "sitemap.png"), "Gambar 6.1 Sitemap PupukPintar dan alur kritis tiga ketukan", 15.0)
    tabel("Tabel 6.1 Halaman utama, tujuan, dan fitur terkait", ["Halaman atau layar", "Tujuan", "Fitur terkait (ID)", "Pengguna"], [
        ["Splash dan onboarding", "Meminta persetujuan data sejak awal", "F-01", "Petani baru"],
        ["Beranda", "Ringkasan lahan aktif, musim tanam, rekomendasi terakhir", "F-02, F-03", "Petani"],
        ["Lahan Saya dan tambah lahan", "Mengelola data lahan sebagai input model", "F-02", "Petani"],
        ["Rekomendasi dan hasil", "Menghasilkan dan meninjau rekomendasi", "F-03 sampai F-06", "Petani"],
        ["Riwayat", "Membandingkan rekomendasi antarmusim", "F-07", "Petani"],
        ["Papan Penyuluhan", "Edukasi dan verifikasi manusia", "F-08", "Petani dan penyuluh"],
        ["Profil dan pengaturan", "Akun, consent, penghapusan data, transparansi model", "F-01", "Semua"],
    ], lebar=[4.0, 5.6, 2.6, 3.8], ukuran=10)
    tabel(None, ["Alur kritis", "Langkah"], [
        ["Beranda sampai hasil", "Buka aplikasi (masuk sekali di awal), pilih petak di Lahan Saya atau langsung ke Rekomendasi, tekan Hitung Rekomendasi, hasil tampil. Tiga ketukan dari beranda, di bawah ambang lima ketukan NFR. Titik yang dulu berpotensi membingungkan adalah pemilihan lahan, diatasi dengan chip lahan dan ringkasan hara yang tampil di formulir"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("6.2 Wireframe dan desain high-fidelity")
    gambar(os.path.join(WIRE, "Layar 1 - Entry Point (Splash & Onboarding).png"), "Gambar 6.2 Wireframe layar 1, entry point (LKP-P6)", 7.6)
    gambar(os.path.join(WIRE, "Layar 2 - Rekomendasi Dosis (Fitur AI Utama).png"), "Gambar 6.3 Wireframe layar 2, formulir rekomendasi (LKP-P6)", 7.6)
    gambar(os.path.join(WIRE, "Layar 3 - Hasil Rekomendasi (Output).png"), "Gambar 6.4 Wireframe layar 3, hasil rekomendasi (LKP-P6)", 7.6)
    tabel("Tabel 6.2 Perubahan wireframe ke desain high-fidelity dan alasannya", ["Layar", "Wireframe low-fidelity", "Desain high-fidelity", "Perubahan dan alasan"], [
        ["Entry point", "Placeholder logo dan ilustrasi abu-abu", "Logo daun NPK, kartu persetujuan bertuliskan jelas, tombol besar (gambar 6.5)", "Placeholder diganti konten nyata, consent dibuat spesifik sesuai rencana privasi LKP-P4"],
        ["Formulir rekomendasi", "Kartu petak statis, input angka", "Chip pemilih lahan dengan ringkasan hara, segmented komoditas, nilai bawaan masuk akal (gambar 6.6)", "Petani tidak perlu mengetik dari nol, alur tiga ketukan terjaga"],
        ["Hasil", "Tiga kartu dosis, badge keyakinan", "Badge keyakinan berpindah ke baris sendiri, kartu dosis diberi sub-label rentang aman, paket mengubah biaya seketika (gambar 6.7)", "Badge di baris judul terpotong pada layar 390 piksel saat uji perjalanan, dipindah agar selalu utuh"],
    ], lebar=[2.6, 4.2, 4.6, 4.6], ukuran=9)
    gambar(os.path.join(LAYAR, "01-splash.png"), "Gambar 6.5 Layar entry point terbangun", 6.4)
    gambar(os.path.join(LAYAR, "08-form-rekomendasi.png"), "Gambar 6.6 Layar formulir rekomendasi terbangun", 6.4)
    gambar(os.path.join(LAYAR, "09-hasil-rekomendasi.png"), "Gambar 6.7 Layar hasil rekomendasi terbangun (padi, target 6 t/ha, luas 0,5 ha, keyakinan 81 persen)", 6.4)
    gambar(os.path.join(LAYAR, "04-peta-hara.png"), "Gambar 6.8 Menggambar petak pada peta vektor 191 area SAFRONS, luas terukur otomatis dari geometri gambaran", 6.4)

    h2("6.3 Tipe antarmuka dan tingkat otomasi")
    tabel(None, ["Pilihan", "Isi dan alasan"], [
        ["Tipe antarmuka", "Hybrid, tulang punggung graphical (peta, formulir, kartu angka) dengan lapisan bahasa sederhana untuk penjelasan, sesuai keputusan LKP-P3. Cocok untuk persona pemakai ponsel yang lebih percaya angka jelas daripada percakapan bebas"],
        ["Tingkat otomasi", "Augmented, AI menyusun rekomendasi, petani meninjau, penyuluh memverifikasi sebelum dijalankan. Manusia memutuskan pada dua titik, yaitu petani memeriksa hasil dan penyuluh menyetujui atau meminta koreksi"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("6.4 Penanganan ketidakpastian")
    tabel("Tabel 6.3 Enam situasi ketidakpastian dan rancangan tampilannya", ["Situasi", "Yang ditampilkan", "Contoh teks pesan", "Fallback"], [
        ["Keyakinan tinggi (0,85 ke atas)", "Badge hijau Keyakinan 91 persen (Yakin), tiga kartu dosis, biaya, paket", "Keyakinan 91% (Yakin)", "Tetap disertai disclaimer dan tombol verifikasi penyuluh"],
        ["Keyakinan sedang (0,70 sampai 0,85)", "Badge kuning Cukup yakin, angka tetap tampil dengan sub-label rentang aman", "Keyakinan 81% (Cukup yakin)", "Petani dianjurkan cek ulang, verifikasi penyuluh makin dianjurkan"],
        ["Keyakinan rendah (di bawah 0,70)", "Tanpa angka, kartu menjelaskan alasan, rentang aman resmi tetap tampil", "Model belum cukup yakin untuk kasus ini. Angka tidak ditampilkan agar tidak salah langkah", "Arahan uji tanah laboratorium atau penyuluh"],
        ["Di luar domain (komoditas selain padi-jagung)", "Penolakan dengan pesan spesifik", "komoditas harus Padi atau Jagung", "Pengguna memilih komoditas yang tersedia"],
        ["Input buruk (misal pH 9,4)", "Validasi menolak dengan daftar galat per medan", "pH=9,4 di luar rentang layak 3,0 sampai 9,0", "Pengguna memperbaiki input"],
        ["Sistem gagal atau offline", "Banner status jaringan, pesan galat, hasil tersimpan tetap aman", "Server tidak terjangkau. Periksa koneksi lalu coba lagi", "Tombol coba lagi, data lokal tidak hilang"],
    ], lebar=[3.0, 4.0, 5.2, 3.8], ukuran=9)
    tabel(None, ["Cara menampilkan confidence", "Alasannya"], [
        ["Bentuk penyajian", "Persentase ditambah kata kategori (Yakin, Cukup yakin) dan kode warna latar. Persen memberi takaran, kata memudahkan petani dengan literasi digital beragam, warna terbaca sekilas. Ambangnya sama dengan Bab 4.4 dan ditetapkan sebelum pengujian"],
    ], lebar=[3.2, 12.8], ukuran=10)
    gambar(os.path.join(LAYAR, "14-hasil-luar-sebaran.png"), "Gambar 6.9 Keadaan input di luar sebaran data latih, angka disembunyikan dan diarahkan ke uji lab", 7.6)

    h2("6.5 Human-in-the-loop")
    tabel("Tabel 6.4 Keputusan berisiko tinggi dan mekanisme eskalasinya", ["Keputusan berisiko tinggi", "Mengapa berisiko", "Pengambil keputusan akhir", "Mekanisme di produk"], [
        ["Menjalankan dosis pupuk", "Salah dosis membuang uang dan bisa meracuni tanaman", "Petani setelah verifikasi penyuluh", "Tombol Kirim ke Penyuluh pada setiap hasil, status verifikasi tampil di riwayat (menunggu, disetujui, minta koreksi)"],
        ["Pengapuran tanah masam", "Dosis kapur salah memengaruhi pH jangka panjang", "Penyuluh", "Pita peringatan pengapuran pada pH di bawah 5,5 dengan anjuran konsultasi penyuluh"],
        ["Input di luar sebaran data latih", "Model tidak punya dasar memprediksi", "Petani dengan bantuan lab atau penyuluh", "Angka disembunyikan, arahan uji lab tampil"],
    ], lebar=[3.4, 4.0, 3.4, 5.2], ukuran=9.5)
    gambar(os.path.join(LAYAR, "12-penyuluhan.png"), "Gambar 6.10 Papan Penyuluhan dengan panel verifikasi penyuluh", 6.4)

    daftar_periksa([
        ["Sitemap dan alur kritis jelas, halaman terkait fitur", "Terpenuhi (Gambar 6.1, Tabel 6.1)"],
        ["Tiga layar utama dalam wireframe dan hi-fidelity", "Terpenuhi (Gambar 6.2 sampai 6.7)"],
        ["Tipe antarmuka dan tingkat otomasi dipilih dengan alasan", "Terpenuhi (6.3)"],
        ["Enam situasi ketidakpastian punya rancangan dan fallback", "Terpenuhi (Tabel 6.3, dibuktikan di Bab 8)"],
        ["Keputusan berisiko tinggi diserahkan ke ahli dengan mekanisme", "Terpenuhi (Tabel 6.4)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 7 IMPLEMENTASI TEKNIS
# ======================================================================
def bab7():
    h1("Bab 7 Arsitektur dan Implementasi Teknis")

    h2("7.1 Tech stack")
    tabel("Tabel 7.1 Lapisan teknologi, alasan, dan alternatif yang ditolak", ["Lapisan", "Teknologi", "Alasan dipilih", "Alternatif yang ditolak dan alasannya"], [
        ["Antarmuka", "HTML, CSS, JavaScript murni, mobile-first 390 piksel", "Tanpa proses build, semua anggota bisa menjalankan, cocok demo di HP lewat browser", "Flutter (rencana awal LKP-P6 untuk rilis Android, tetap dipertimbangkan untuk versi APK), Next.js (butuh ekosistem build yang tidak perlu untuk MVP)"],
        ["Server API", "Pustaka standar Python http.server", "Kontrak API identik dengan rencana FastAPI, tanpa dependensi biner yang diblokir kebijakan mesin (Bab 7.6)", "FastAPI dipertahankan sebagai rencana penyebaran produksi, migrasinya langsung karena kontrak sama"],
        ["Model AI", "Random Forest Regressor scikit-learn 1.8, diekspor joblib", "Lulus PoC dan holdout, feature importance membantu penjelasan, tidak butuh GPU", "Gradient Boosting (risiko overfit pada proxy, penjelasan lebih rumit), model deep learning (data terlalu kecil, tidak proporsional)"],
        ["Basis data", "localStorage pada versi demo", "Tanpa server basis data, data tetap di perangkat petani sesuai prinsip minimisasi", "PostgreSQL (rencana produksi saat fitur penyuluh daring), SQLite (alternatif lokal)"],
        ["Hosting", "Lokal untuk demo, rencana VPS kecil", "Belum ada akun hosting tim, biaya dihitung di Bab 9", "Vercel gratis (cocok statis, tetapi model Python butuh runtime server)"],
        ["Repositori", "GitHub", "Publik, berisi seluruh kode, pengujian, laporan, dan presentasi", "Tidak ada alternatif yang dibahas"],
    ], lebar=[2.2, 3.4, 4.4, 6.0], ukuran=9)

    h2("7.2 Arsitektur sistem")
    gambar(os.path.join(GAMBAR, "gambar", "arsitektur.png"), "Gambar 7.1 Arsitektur sistem dari input pengguna sampai keluaran model", 15.5)
    p("Alur lengkap: petani mengisi formulir di antarmuka, JavaScript mengirim POST /rekomendasi berisi sembilan field, server memvalidasi input lewat fungsi validasi, mesin model.py menjalankan prediksi Random Forest dan menghitung keyakinan dari sebaran prediksi antarpohon, guardrail mengunci dosis pada rentang Permentan, aturan Balittanah menambah peringatan, lalu server menyusun JSON jawaban yang memuat dosis, keyakinan, kebutuhan per petak, biaya, paket, penjelasan, dan disclaimer.")

    h2("7.3 Kontrak API")
    tabel("Tabel 7.2 Kontrak API model AI", ["Endpoint", "Metode", "Input (format)", "Output (format)"], [
        ["/rekomendasi", "POST", "JSON 9 field: pH, n_persen, p_ppm, k_me100g, tekstur, komoditas, target_hasil_t_ha, luas_ha, musim", "JSON: masukan, status_hara, keyakinan, kategori_keyakinan, luar_sebaran_data_latih, tampilkan_angka, dosis_kg_ha (atau null), rentang_aman_kg_ha, kebutuhan_petak_kg, estimasi_biaya_idr, paket (hemat, standar, optimal), peringatan, penjelasan, disclaimer, waktu_proses_ms"],
        ["/model/info", "GET", "Tanpa body", "JSON metrik CV, holdout, latensi, feature importance"],
        ["/api/peta", "GET", "Tanpa body", "JSON 191 area SAFRONS: nama, pH rata-rata, band dan nilai perwakilan N-P-K, tekstur, geometri ringkas"],
        ["/api/health", "GET", "Tanpa body", "JSON status layanan dan kesiapan model"],
    ], lebar=[2.4, 1.4, 5.2, 7.0], ukuran=9)
    p("Contoh permintaan dan respons nyata dari aplikasi yang berjalan:")
    kode('POST /rekomendasi\n{"pH": 5.4, "n_persen": 0.35, "p_ppm": 7.0, "k_me100g": 0.18,\n "tekstur": "Lempung", "komoditas": "Padi",\n "target_hasil_t_ha": 6.0, "luas_ha": 0.5, "musim": "Hujan"}')
    kode('Respons nyata dari server (dipangkas, dapat diulang lewat curl sesuai README)\n{"status_hara": {"N": "Sedang", "P": "Rendah", "K": "Rendah"},\n "keyakinan": 0.81, "kategori_keyakinan": "sedang",\n "tampilkan_angka": true,\n "dosis_kg_ha": {"N": 217, "P": 83, "K": 51},\n "kebutuhan_petak_kg": {"Urea": 236, "SP36": 138, "KCl": 42},\n "estimasi_biaya_idr": 1058400,\n "peringatan": ["Tanah masam (pH 5,4). Pertimbangkan pengapuran karena fosfor mudah terikat.",\n                "Musim hujan: bagi pemupukan urea menjadi dua tahap agar nitrogen tidak tercuci."],\n "penjelasan": "Dosis N sedang karena stok nitrogen lahan Anda sedang. ...",\n "waktu_proses_ms": 63.3}')
    p("Angka pada contoh di atas adalah respons sebenarnya dari server dan persis sama dengan tangkapan layar Gambar 6.7 (lahan uji tanah pH 5,4, luas 0,5 ha). Penyimpangan dari kontrak LKP-P6 hanya penambahan field paket, penjelasan, kategori_keyakinan, dan waktu_proses_ms, tanpa mengubah field lama.")

    h2("7.4 Hasil proof-of-concept dibanding target")
    tabel("Tabel 7.3 Kelayakan PoC (LKP-P6) dibanding target SRS", ["Pertanyaan kelayakan", "Target", "Hasil nyata", "Selisih dan tindakan"], [
        ["Apakah model mencapai agreement pakar minimal 85 sampai 90 persen?", "85 sampai 90 persen", f"PoC CV {str(POC['agreement_persen']).replace('.', ',')} persen, final CV {str(CV['agreement_persen']).replace('.', ',')} persen, holdout {str(HOLD['agreement_persen']).replace('.', ',')} persen", "Melampaui target, dilanjutkan ke implementasi penuh"],
        ["Apakah latensi memadai (kurang dari 5 detik)?", "Kurang dari 5 detik", "Model 63,8 ms (p95), API lengkap 87 ms (p95 dari 30 permintaan)", "Jauh di bawah target"],
        ["Apakah sistem menolak kasus meragukan?", "Angka tidak ditampilkan pada kasus ragu", "Uji pH 9,4 ditolak validasi, P 150 ppm ditandai luar sebaran tanpa angka", "Terpenuhi, diuji otomatis di pytest"],
        ["Apakah data proxy cukup?", "Cukup untuk validasi alur", "Cukup untuk alur, tetapi bukan pengganti data lapangan", "Validasi lapangan jadwalkan bersama poktan (Bab 11)"],
    ], lebar=[4.6, 3.0, 4.6, 3.8], ukuran=9.5)
    gambar(os.path.join(REPO, "poc", "grafik_poc.png"), "Gambar 7.2 Ringkasan hasil PoC, agreement melampaui target SRS dan galat per unsur", 14.5)

    h2("7.5 Hasil build")
    tabel("Tabel 7.4 Bukti fitur Must berjalan end-to-end pada aplikasi", ["ID fitur", "Bukti", "End-to-end?", "Catatan"], [
        ["F-01", "Gambar 6.5 dan langkah uji perjalanan splash sampai beranda", "Ya", "Consent wajib dicentang sebelum masuk"],
        ["F-02", "Gambar 6.8 (peta hara SAFRONS) dan langkah lahan dari peta serta uji tanah", "Ya", "Dua jalur input teruji, validasi pH 9,4 menolak"],
        ["F-03", "Gambar 6.7 dan respons API contoh di 7.3", "Ya", "Dosis, keyakinan, guardrail tampil"],
        ["F-04", "Gambar 6.7 dan langkah paket optimal mengubah biaya", "Ya", "Hemat, standar, optimal mengubah kebutuhan dan biaya"],
    ], lebar=[1.4, 7.0, 2.0, 5.6], ukuran=9.5)
    tabel(None, ["Repositori dan aplikasi", "Keterangan"], [
        ["Repositori", TAUTAN["github"] + " , struktur: app (backend dan frontend), poc, tests, docs, laporan, presentasi. README memuat cara menjalankan tiga langkah"],
        ["Aplikasi berjalan", "Demo lokal http://127.0.0.1:8000, tanpa login, dijalankan dengan python server.py dari folder app/backend setelah train.py sekali dijalankan"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("7.6 Kendala teknis dan keputusan")
    tabel("Tabel 7.5 Kendala, opsi yang dipertimbangkan, keputusan, dan dampaknya", ["Kendala", "Opsi yang dipertimbangkan", "Keputusan", "Alasan dan dampak"], [
        ["Kebijakan Application Control pada mesin anggota memblokir ekstensi biner pydantic-core (dependensi FastAPI) dan sebagian versi scikit-learn", "Cari pengecualian kebijakan, ganti mesin, atau bangun server tanpa dependensi biner", "Server demo ditulis dengan pustaka standar http.server, scikit-learn dipasang versi 1.8 yang tidak diblokir", "Kontrak API tidak berubah sehingga migrasi ke FastAPI saat produksi bersih. Konvensi endpoint, status 422, dan bentuk galat dipertahankan identik"],
        ["Koordinat peta SAFRONS ternyata tersimpan dalam proyeksi UTM meter meski berkas .prj mengaku WGS84, dan satuan N-P-K tidak dideklarasikan pada sumbernya", "Memakai apa adanya (peta melenceng), menunggu kepastian satuan, atau mengonversi sendiri dengan dokumentasi lengkap", "Konversi UTM 48S ke WGS84 memakai rumus Transverse Mercator inverse (gen_peta.py), dan N-P-K dipetakan dari band kuintil SAFRONS ke nilai perwakilan skala model (Lampiran C)", "Peta sungguhan 191 area terpakai di demo, konversi dapat diperiksa siapa pun, status hara hasil peta konsisten dengan interpretasi Balittanah kami"],
        ["Model bahasa untuk penjelasan menambah biaya dan risiko halusinasi angka", "Pakai LLM API, atau templat rule-based", "Templat rule-based dari status hara dan musim", "Penjelasan selalu sesuai angka model, biaya nol, latensi nol"],
        ["Label berasal dari logika aturan sehingga model belajar dari aturan yang sama", "Menghentikan proyek, atau jujur memakai proxy dengan rencana data lapangan", "Melanjutkan dengan proxy dan mencatat keterbatasan secara eksplisit", "Ini keterbatasan inti produk (Bab 12.2), data uji tanah dan catatan panen menjadi prioritas pilot"],
    ], lebar=[4.2, 3.8, 3.6, 4.4], ukuran=9)

    daftar_periksa([
        ["Setiap pilihan teknologi punya alasan dan alternatif ditolak", "Terpenuhi (Tabel 7.1)"],
        ["Diagram arsitektur memuat alur input sampai output", "Terpenuhi (Gambar 7.1)"],
        ["Kontrak API dan contoh JSON nyata", "Terpenuhi (Tabel 7.2 dan contoh)"],
        ["PoC dibanding target termasuk yang belum tercapai", "Terpenuhi (Tabel 7.3, baris data proxy)"],
        ["Setiap fitur Must punya bukti end-to-end", "Terpenuhi (Tabel 7.4)"],
        ["Tautan repositori dan aplikasi bisa dibuka", "Repositori publik, aplikasi berjalan lokal dengan cara tersedia di README"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 8 PENGUJIAN
# ======================================================================
def bab8():
    h1("Bab 8 Pengujian dan Evaluasi")

    h2("8.1 Rancangan uji")
    p("Tujuan dan hipotesis uji: model mencapai agreement pakar minimal 85 sampai 90 persen pada data yang tidak dipakai melatih, guardrail tidak pernah melepas keluaran di luar rentang aman, dan petani dengan literasi digital umum menyelesaikan alur dari beranda sampai hasil dalam maksimal lima ketukan tanpa tersesat.")
    p("Waktu dan cara uji: pengujian model dan API berlangsung terotomasi pada mesin pengembangan (pytest, 12 pengujian), pengujian antarmuka berlangsung terotomasi dengan Playwright pada Chromium lebar 390 piksel (20 langkah), dan pengukuran latensi API berlangsung dengan 30 permintaan beruntun. Semua uji dapat diulang dengan perintah pada README repositori.")
    tabel("Tabel 8.1 Profil penguji dan kedudukannya", ["Kode", "Peran", "Keterangan", "Catatan jujur"], [
        ["U-01 sampai U-03", "Anggota tim sebagai penguji alur (tiga orang)", "Menjalankan dan memeriksa 18 langkah uji perjalanan", "Anggota tim bukan pengguna sasaran. Uji petani sasaran dijadwalkan pada pilot Bab 11, status ini juga dicatat di Bab 12.2"],
    ], lebar=[2.6, 4.2, 5.2, 4.0], ukuran=9.5)
    tabel("Tabel 8.2 Skenario uji", ["ID", "Skenario atau tugas", "Fitur (ID)", "Kriteria berhasil"], [
        ["S-01", "Masuk aplikasi tanpa mencentang persetujuan lalu dengan mencentang", "F-01", "Pesan galat tampil tanpa centang, masuk berhasil dengan centang"],
        ["S-02", "Menggambar petak 4 titik di peta lalu menyimpannya, termasuk uji mode pilih unit dengan klik koordinat", "F-02", "Luas terukur otomatis tampil pada gambaran uji (sekitar 0,5 ha), lahan tersimpan berlabel dari gambar peta"],
        ["S-03", "Mendaftar lahan dari uji tanah, termasuk percobaan pH 9,4", "F-02", "pH 9,4 ditolak dengan pesan, input wajar tersimpan"],
        ["S-04", "Menghitung rekomendasi padi pada lahan uji tanah, mengganti paket optimal, mengirim ke penyuluh, membuka riwayat", "F-03 sampai F-07", "Hasil tampil, paket mengubah biaya, riwayat terisi"],
        ["S-05", "Menghitung rekomendasi pada lahan dengan P 150 ppm (luar sebaran)", "F-03, F-06", "Angka disembunyikan, arahan uji lab tampil"],
        ["S-06", "Menghitung rekomendasi jagung pada lahan normal", "F-03", "Dosis dalam rentang jagung, badge keyakinan tampil"],
        ["S-07", "Meninjau verifikasi sebagai penyuluh lalu menyetujui", "F-08", "Item keluar dari daftar menunggu, status berubah"],
    ], lebar=[1.0, 6.6, 2.4, 6.0], ukuran=9.5)

    h2("8.2 Hasil keandalan AI")
    tabel("Tabel 8.3 Hasil keandalan model dan sistem", ["Metrik", "Cara mengukur", "Target (Bab 4.4)", "Hasil", "Lolos?"], [
        ["Agreement (CV 5-fold)", "cross_val_predict pada 6.000 baris", "85 sampai 90 persen", f"{str(CV['agreement_persen']).replace('.', ',')} persen (N 100, P 98,6, K 95,8)", "Ya"],
        ["Agreement (holdout)", "1.200 baris yang tidak dipakai melatih (seed 7)", "85 sampai 90 persen", f"{str(HOLD['agreement_persen']).replace('.', ',')} persen (N 100, P 98,2, K 96,5)", "Ya"],
        ["MAE per unsur", "Holdout", "Di bawah 10 persen dosis rata-rata", "N 3,6, P 2,4, K 2,1 kg/ha", "Ya"],
        ["Guardrail rentang aman", "45 kombinasi input ekstrem padi dan uji jagung pada pytest", "0 keluaran di luar rentang", "Semua dalam rentang, lulus", "Ya"],
        ["Penolakan input buruk", "pH 9,4, komoditas Cabai, pH string lima", "Ditolak dengan pesan per medan", "Semua berstatus 422 dengan pesan jelas", "Ya"],
        ["Kasus luar sebaran", "P 150 ppm pada pytest dan skenario S-05 UI", "Angka disembunyikan", "tampilkan_angka false, arahan uji lab tampil", "Ya"],
        ["Determinisme", "Dua permintaan identik", "Hasil identik", "Identik penuh", "Ya"],
        ["Latensi API", "30 permintaan beruntun", "Kurang dari 5 detik", "Rata-rata 71 ms, p95 87 ms, maksimal 90 ms", "Ya"],
    ], lebar=[3.2, 4.2, 2.6, 4.6, 1.4], ukuran=9)
    tabel(None, ["Set uji keandalan", "Keterangan pemisahan data"], [
        ["Data uji", "Holdout 20 persen (1.200 baris) dipisah dengan seed 7, berbeda dari seed pelatihan 42, dan tidak pernah disentuh saat pemilihan model. Uji silang 5-fold dijalankan terpisah pada seluruh data sebagai pembanding dengan PoC"],
    ], lebar=[3.2, 12.8], ukuran=10)
    p("Analisis kalibrasi keyakinan pada data holdout:")
    tabel("Tabel 8.4 Kalibrasi keyakinan per kelompok (holdout)", ["Kelompok keyakinan", "Proporsi kasus", "Keyakinan rata-rata", "Agreement terukur"], [
        ["0,85 ke atas (Yakin)", "98,8 persen", "0,93", "95,8 persen"],
        ["0,70 sampai 0,85 (Cukup yakin)", "1,2 persen", "0,83", "42,9 persen"],
        ["Di bawah 0,70 (Tidak yakin)", "0 persen pada holdout", "Tidak ada kasus", "Tidak ada kasus"],
    ], lebar=[4.6, 3.2, 3.4, 4.8], ukuran=10)

    h2("8.3 Hasil usability dan kepercayaan")
    tabel("Tabel 8.5 Hasil uji perjalanan antarmuka (20 langkah, Chromium 390 piksel)", ["Metrik", "Cara mengukur", "Hasil"], [
        ["Tingkat keberhasilan langkah", "Langkah lulus dibagi seluruh langkah", "20 dari 20 (100 persen)"],
        ["Alur kritis tiga ketukan", "Penghitungan ketukan pada skenario S-04", "3 ketukan dari beranda sampai hasil"],
        ["Kejadian tersesat atau galat konsol", "Perekaman konsol browser selama perjalanan", "Nol galat konsol"],
        ["Luapan tampilan", "Pengukuran scrollWidth pada empat layar kunci", "Nol piksel luapan"],
        ["Kontrol yang mati", "Perjalanan klik pada setiap tombol, chip, segmen, panel verifikasi", "Semua kontrol punya efek nyata (paket mengubah biaya, verifikasi mengubah status, dst)"],
    ], lebar=[4.0, 6.4, 5.6], ukuran=9.5)
    p("Dari sisi kepercayaan, seluruh hasil memuat badge keyakinan, penjelasan, dan disclaimer, dan sistem berani menyembunyikan angka pada kasus luar sebaran (Gambar 6.9). Dua hal ini menurut kami adalah fondasi kepercayaan yang paling penting sebelum pilot.")

    h2("8.4 Temuan dan analisis gap")
    tabel("Tabel 8.6 Temuan pengujian beserta gap dan tindak lanjutnya", ["Temuan", "Bukti", "Gap terhadap ekspektasi", "Tingkat keparahan", "Tindak lanjut"], [
        ["Keyakinan pita tengah tidak terkalibrasi baik", "Tabel 8.4, agreement terukur 42,9 persen pada kelompok Cukup yakin yang mengaku 0,83", "Kalibrasi diharapkan mendekati angka keyakinan", "Sedang", "Kategori sedang tetap diberi sub-label rentang dan anjuran cek ulang, kalibrasi ulang menunggu data lapangan, diamati lagi saat pilot"],
        ["Hampir semua kasus dalam sebaran masuk kelompok Yakin (98,8 persen)", "Tabel 8.4", "Diharapkan sebaran keyakinan lebih beragam", "Rendah", "Wajar untuk data proxy yang bersih, uji ulang pada data lapangan yang lebih bising"],
        ["Badge keyakinan terpotong pada layar sempit", "Uji perjalanan langkah hasil, tangkapan layar sebelum perbaikan", "Teks keluar kontainer pada 390 piksel", "Sedang", "Badge dipindah ke baris sendiri, uji ulang lulus tanpa luapan (iterasi di 8.5)"],
        ["Peta grid awal berupa representasi buatan, bukan data asli", "Perbandingan peta versi awal dengan data sumber SAFRONS", "Input lahan tidak memakai peta sungguhan", "Rendah", "Diganti peta spasial asli 191 area SAFRONS setelah data ditemukan di repositori audit"],
        ["Konversi kebutuhan petak tidak bisa dihitung ulang dari angka tampilan", "Uji konsistensi konversi pytest gagal di versi awal", "Petani tidak bisa memeriksa 71 kg/ha kali 0,75 ha dibagi 0,30", "Sedang", "Dosis dibulatkan sejak awal sehingga semua turunan konsisten, uji lulus"],
        ["Area terpilih pada peta kadang tidak sesuai poligon yang dituju pengguna", "Laporan pengguna saat mencoba peta, dikonfirmasi perbandingan titik klik dengan area terpilih", "Pengguna menekan poligon A tetapi kartu detail menunjukkan area lain", "Sedang", "Pemilihan area dihitung dari titik ketuk memakai uji titik-dalam-poligon, highlight dipindah ke lapisan non-interaktif, dan opsi tap peta dihapus. Verifikasi otomatis: klik titik -6,6 106,8 kini selalu memilih area Bogor"],
        ["Unit lanskap SAFRONS berukuran besar sehingga tidak mewakili petak petani", "Perbandingan bentuk unit lanskap dengan petak tipikal 0,25 sampai 2 hektar", "Bentuk dan luas lahan terpilih tidak sesuai lahan nyata pengguna", "Tinggi", "Alat gambar petak ditambahkan sebagai jalur utama F-02: petani melukis batasnya, luas dihitung geodesik dari geometri, nilai hara dari unit tempat pusat petak"],
        ["Latar peta daring (tile OpenStreetMap) membuat tampilan peta tidak konsisten di sebagian peramban", "Tile gagal atau terlambat dimuat pada webview sehingga latar peta patah di balik poligon", "Peta terlihat rusak dan menambah dependensi jaringan pada demo", "Sedang", "Basemap daring dihapus bersama pustaka Leaflet, peta dibangun ulang sebagai kanvas vektor SVG mandiri yang bebas internet dan konsisten di semua peramban"],
    ], lebar=[4.0, 3.8, 3.6, 1.8, 4.0], ukuran=9)

    h2("8.5 Iterasi yang dilakukan")
    tabel("Tabel 8.7 Iterasi perbaikan beserta alasannya", ["Iterasi", "Perubahan", "Alasan (dari temuan)"], [
        ["1", "Badge keyakinan pindah ke baris tersendiri pada layar hasil", "Temuan terpotong pada 390 piksel"],
        ["2", "Peta grid 12 zona diganti peta spasial asli 191 area SAFRONS", "Data asli ditemukan di repositori audit sehingga representasi buatan tidak lagi diperlukan"],
        ["3", "Dosis dibulatkan ke kg/ha utuh sebelum konversi kebutuhan dan biaya", "Uji konsistensi konversi, agar petani bisa memeriksa ulang angka"],
        ["4", "Luas petak selalu terisi dari lahan terpilih", "Konsistensi nilai bawaan formulir"],
        ["5", "Pemilihan area peta berbasis titik ketuk dengan highlight non-interaktif", "Laporan ketidaksesuaian area terpilih pada peta"],
        ["6", "Alat gambar petak ditambahkan sebagai jalur utama pendaftaran lahan, luas terukur otomatis dari geometri", "Unit lanskap SAFRONS berbentuk besar dan tidak mewakili petak individu"],
        ["7", "Peta dibangun ulang sebagai kanvas vektor SVG mandiri tanpa Leaflet dan tanpa tile daring, lengkap dengan pan, zum, dan tooltip sendiri", "Latar daring membuat UI peta tidak konsisten dan rentan kegagalan jaringan"],
    ], lebar=[1.4, 7.0, 7.6], ukuran=9.5)

    h2("8.6 Status akhir MVQ")
    tabel(None, ["Pernyataan status MVQ", "Keterangan"], [
        ["Tercapai untuk enam dimensi teknis", "Ketepatan, waktu respons, keamanan keluaran, cakupan domain, explainability, dan keamanan keputusan berisiko lolos seluruh ujinya (Tabel 4.4 dan Tabel 8.3)"],
        ["Belum untuk kepuasan petani", "Dimensi kepuasan minimal 4 dari 5 butuh pengguna sasaran. Menunggu pilot poktan, dan selama itu statusnya jujur kami laporkan belum, bukan mengarang angka"],
    ], lebar=[4.6, 11.4], ukuran=10)

    daftar_periksa([
        ["Pengguna uji dijelaskan profil dan kedudukannya", "Terpenuhi, termasuk pengakuan bahwa petani sasaran belum menjadi penguji"],
        ["Setiap metrik MVQ diuji dan dilaporkan", "Terpenuhi (Tabel 8.3)"],
        ["Data uji terpisah dari data latih", "Terpenuhi (holdout seed 7, keterangan di 8.2)"],
        ["Temuan buruk dilaporkan", "Terpenuhi (Tabel 8.6, lima temuan dengan parahan)"],
        ["Tiap iterasi dikaitkan temuan", "Terpenuhi (Tabel 8.7)"],
        ["Data mentah dan formulir umpan balik di lampiran", "Terpenuhi (Lampiran D)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 9 EKONOMI AI
# ======================================================================
def bab9():
    h1("Bab 9 Ekonomi AI")

    p("PupukPintar versi ini tidak memakai LLM pada jalur utama. Sesuai panduan produk non-LLM, biaya yang dihitung adalah biaya inferensi dan hosting per prediksi, yaitu biaya server per bulan dibagi jumlah prediksi per bulan. Untuk pembanding, kami juga menghitung skenario bila penjelasan kelak memakai LLM.")

    h2("9.1 Asumsi biaya")
    tabel("Tabel 9.1 Parameter dan dasar asumsi", ["Parameter", "Simbol", "Nilai", "Dasar asumsi dan sumber"], [
        ["Biaya server kecil", "S", "Rp 90.000 per bulan", "Asumsi harga VPS 1 CPU 1 GB dari penyedia lokal (nilai yang lazim di pasar Indonesia, ditetapkan sebagai asumsi tim karena belum ada akun hosting). Belum ada tagihan nyata karena demo berjalan lokal"],
        ["Kueri rekomendasi per petani per bulan musim tanam", "Q", "5", "Perkiraan dari pola pakai: 1 sampai 2 rekomendasi baru ditambah cek ulang sebelum beli pupuk (asumsi tim)"],
        ["Panjang musim tanam aktif", "M", "3 bulan", "Puncak musim hujan Oktober sampai Maret di Bogor (LKP-P4)"],
        ["Jumlah petani per poktan", "N", "25", "Ukuran poktan yang lazim (asumsi tim untuk pilot)"],
        ["Harga LLM bila kelak dipakai untuk penjelasan", "P", "sekitar Rp 15 per 1.000 token keluaran pada model kelas hemat", "Asumsi dari kisaran harga API model hemat penyedia besar, ditetapkan sebagai asumsi, belum ada log token karena jalur LLM tidak dipakai"],
        ["Pembanding biaya uji tanah lab", "L", "Rp 150.000 per sampel", "Asumsi umum harga analisis tanah sederhana (asumsi tim, perlu konfirmasi saat pilot)"],
    ], lebar=[4.4, 1.4, 3.4, 6.8], ukuran=9)

    h2("9.2 Perhitungan biaya")
    p("Rumus produk non-LLM: biaya per prediksi = biaya server per bulan dibagi jumlah prediksi per bulan, dengan jumlah prediksi per bulan = jumlah petani kali kueri per bulan.")
    tabel("Tabel 9.2 Tiga skenario biaya operasional", ["Skenario", "Petani", "Prediksi per bulan", "Biaya bulanan", "Biaya per prediksi", "Biaya per petani per bulan"], [
        ["Konservatif (pilot 1 poktan)", "25", "125", "Rp 90.000", "Rp 720", "Rp 3.600"],
        ["Realistis (4 poktan)", "100", "500", "Rp 90.000", "Rp 180", "Rp 900"],
        ["Optimistis (20 poktan)", "500", "2.500", "Rp 180.000 (server lebih besar)", "Rp 72", "Rp 360"],
    ], lebar=[3.6, 1.8, 2.8, 3.0, 2.4, 2.4], ukuran=9.5)
    tabel(None, ["Contoh hitungan lengkap (skenario konservatif)", "Langkah"], [
        ["Jumlah prediksi", "25 petani kali 5 kueri per bulan = 125 prediksi per bulan"],
        ["Biaya per prediksi", "Rp 90.000 dibagi 125 = Rp 720 per prediksi"],
        ["Biaya per petani per bulan", "Rp 90.000 dibagi 25 = Rp 3.600"],
        ["Pembanding", "Satu uji tanah lab Rp 150.000 setara 208 prediksi pada skenario ini"],
    ], lebar=[5.2, 10.8], ukuran=10)
    p("Bila penjelasan kelak memakai LLM (skenario alternatif), perkiraan kasar per rekomendasi sekitar 250 token keluaran dan 400 token masukan, sehingga sekitar Rp 8 per rekomendasi pada asumsi harga di Tabel 9.1. Angka ini masih di bawah biaya server, tetapi kami memilih jalur tanpa LLM untuk menekan risiko halusinasi angka, bukan semata biaya.")

    h2("9.3 Biaya selain server")
    tabel("Tabel 9.3 Komponen biaya lain", ["Komponen", "Penyedia atau pelaksana", "Biaya", "Catatan"], [
        ["Pelatihan ulang model tiap musim", "Tim, laptop biasa", "Rp 0", "Pelatihan 6.000 baris selesai dalam sekitar 4 detik tanpa GPU"],
        ["Domain (bila dipublikasikan)", "Registrar", "sekitar Rp 200.000 per tahun", "Asumsi, opsional saat pilot"],
        ["Sosialisasi bersama poktan", "Tim dan penyuluh", "Transport lokal", "Diluar biaya teknologi, direncanakan dari anggaran kegiatan kuliah"],
    ], lebar=[4.4, 4.2, 3.0, 4.4], ukuran=9.5)

    h2("9.4 Strategi menekan biaya")
    tabel("Tabel 9.4 Strategi penghematan dan kaitannya dengan arsitektur Bab 7", ["Strategi", "Penerapan di produk", "Perkiraan penghematan"], [
        ["Model kecil tanpa GPU", "Random Forest 300 pohon berukuran belasan MB, inferensi in-process dalam server yang sama", "Tidak perlu layanan model terpisah atau GPU, satu server cukup"],
        ["Penjelasan berbasis templat, bukan LLM", "Field penjelasan disusun rule-based di model.py", "Biaya token nol pada jalur utama"],
        ["Data peta statis", "Peta 191 area disajikan dari berkas GeoJSON statis ringkas lewat GET /api/peta", "Tidak ada query basis data per kunjungan peta"],
        ["Pelatihan musiman berbatch", "train.py dijalankan per musim, bukan pelatihan daring", "Biaya komputasi pelatihan nyaris nol"],
    ], lebar=[4.2, 7.0, 4.8], ukuran=9.5)

    h2("9.5 Model bisnis dan titik impas")
    tabel(None, ["Aspek", "Isi"], [
        ["Siapa yang membayar", "Tahap pilot: tidak ada (gratis untuk petani dan poktan). Setelah fitur rekap kelompok jalan: poktan atau koperasi berlangganan, petani tetap gratis"],
        ["Skema dan harga (rencana)", "Iuran layanan poktan Rp 25.000 per bulan mencakup rekap kebutuhan pupuk anggota dan dukungan penyuluhan. Skema ini asumsi tim yang perlu divalidasi kesediaan bayarnya saat pilot"],
        ["Bukti kesediaan membayar", "Belum ada, jujur kami nyatakan sebagai asumsi. Pembandingnya adalah waktu penyusunan RDKK manual yang memakan waktu poktan setiap tahun"],
        ["Titik impas", "Biaya bulanan Rp 90.000 dibagi iuran Rp 25.000 = 3,6, dibulatkan 4 poktan berlangganan menutup biaya server pada skenario konservatif"],
    ], lebar=[3.6, 12.4], ukuran=10)

    daftar_periksa([
        ["Setiap asumsi punya sumber", "Terpenuhi, semua ditandai eksplisit sebagai asumsi tim atau publikasi"],
        ["Tiga skenario dihitung dengan satu contoh lengkap", "Terpenuhi (Tabel 9.2)"],
        ["Biaya non-token disertakan", "Terpenuhi (Tabel 9.3)"],
        ["Strategi penghematan terhubung arsitektur", "Terpenuhi (Tabel 9.4)"],
        ["Titik impas dihitung dan selaras Lean Canvas", "Terpenuhi, konsisten dengan baris revenue stream Bab 2.5"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 10 GOVERNANCE
# ======================================================================
def bab10():
    h1("Bab 10 Governance, Etika, dan Keamanan")

    h2("10.1 Daftar risiko")
    tabel("Tabel 10.1 Risiko produk (R rendah, S sedang, T tinggi)", ["Risiko", "Contoh konkret di produk", "Peluang", "Dampak", "Mitigasi", "Penanggung jawab"], [
        ["Prediksi keliru", "Dosis N berlebih untuk tanah subur di luar sebaran data latih", "S", "T", "Guardrail rentang aman, penanda luar sebaran, verifikasi penyuluh (teruji Bab 8)", "Tim model (Irgi)"],
        ["Ketergantungan berlebih pada AI", "Petani menjalankan angka tanpa membaca peringatan pengapuran", "S", "T", "Badge keyakinan dan kata kategori, pita peringatan, disclaimer permanen, jalur penyuluh", "Tim UX (Thogianna)"],
        ["Bias data", "Petani di luar rentang Bogor atau lahan ekstrem kurang terwakili di data latih", "S", "S", "Penanda input di luar sebaran, pengumpulan data pilot bertahap", "Tim model (Irgi)"],
        ["Salah paham angka", "Petani menganggap kg/ha adalah kebutuhan total petaknya", "S", "S", "Layar hasil selalu menampilkan dua tingkat, kg/ha dan kg per petak, dengan luas tertulis", "Tim UX (Thogianna)"],
        ["Sistem atau data tidak tersedia", "Server mati menjelang pembelian pupuk", "S", "S", "Pesan galat jelas, riwayat lokal tetap terbaca, arahan ke penyuluh", "Tim server (Syarif)"],
        ["Penyalahgunaan data lokasi lahan", "Koordinat petak membocorkan nilai ekonomi lahan", "R", "T", "Versi demo menyimpan data di perangkat petani, tidak ada server penyimpanan koordinat", "Tim server (Syarif)"],
    ], lebar=[2.8, 4.4, 1.4, 1.4, 4.6, 1.8], ukuran=9)

    h2("10.2 Safety guardrail dan disclaimer")
    tabel("Tabel 10.2 Guardrail dan status pengujian", ["Guardrail", "Cara kerja di produk", "Sudah diuji Bab 8?"], [
        ["Kunci rentang aman resmi", "Seluruh dosis (termasuk paket) dikunci rentang Permentan per komoditas sebelum dikirim", "Ya, uji guardrail 45 kombinasi"],
        ["Penolakan input buruk", "Validasi rentang tiap medan, komoditas di luar padi-jagung ditolak", "Ya, uji input buruk"],
        ["Penanda luar sebaran data latih", "pH, N, P, K, dan target hasil dibanding sebaran latih, bila di luar maka angka disembunyikan", "Ya, uji luar sebaran"],
        ["Ambang keyakinan", "Keyakinan di bawah 0,70 tidak menampilkan angka", "Ya, jalur tampilkan_angka false"],
        ["Peringatan dini Balittanah", "Pengapuran pada pH di bawah 5,5, pengapuran wajib pada di bawah 4,5, pembagian urea musim hujan", "Ya, uji peringatan pH masam"],
        ["Disclaimer permanen", "Setiap jawaban API dan layar hasil memuat disclaimer", "Ya, uji kontrak"],
    ], lebar=[3.6, 8.4, 4.0], ukuran=9.5)
    tabel(None, ["Teks disclaimer persis yang tampil ke pengguna", "Isi"], [
        ["Disclaimer hasil", "Rekomendasi awal dari model, bukan pengganti uji tanah laboratorium. Verifikasi penyuluh sebelum pembelian pupuk."],
        ["Pesan luar sebaran", "Kondisi lahan di luar sebaran data latih. Sistem tidak menampilkan angka. Sebaiknya lakukan uji tanah laboratorium."],
    ], lebar=[4.6, 11.4], ukuran=10)

    h2("10.3 Privasi dan persetujuan pengguna")
    tabel("Tabel 10.3 Data sensitif dan minimisasinya", ["Data sensitif", "Alasan dikumpulkan", "Minimisasi", "Penyimpanan dan akses", "Retensi"], [
        ["Kondisi hara lahan (pH, N, P, K, tekstur, luas)", "Input utama model rekomendasi", "Tidak ada medan identitas pada formulir, nama lahan bebas dibuat samar oleh petani", "localStorage perangkat petani, tidak dikirim ke pihak lain", "Sampai petani menghapus dari Profil"],
        ["Persetujuan dan opsi pelatihan model", "Kepatuhan consent", "Satu bita status, tanpa profil terlacak", "localStorage perangkat", "Sampai dihapus"],
    ], lebar=[3.6, 3.2, 4.0, 3.4, 1.8], ukuran=9)
    tabel(None, ["Teks persetujuan persis yang tampil saat onboarding", "Isi"], [
        ["Persetujuan data", "Data lahan Anda dipakai untuk rekomendasi pribadi dan perbaikan model. Identitas disamarkan dan bisa dihapus kapan saja dari halaman Profil. (kotak centang: Saya setuju data saya dipakai sebagaimana dijelaskan)"],
        ["Mekanisme menolak dan menghapus", "Profil memuat saklar bolehkan data lahan saya dipakai memperbaiki model yang dapat dimatikan kapan saja, dan tombol Hapus semua data saya yang membersihkan lahan, riwayat, dan verifikasi di perangkat"],
    ], lebar=[4.6, 11.4], ukuran=10)

    h2("10.4 Bias dan keadilan")
    p("Kelompok yang berpotensi dirugikan: petani dengan kondisi lahan ekstrem yang jarang ada di data latih bisa menerima rekomendasi kurang pas, petani di luar Bogor memakai aplikasi di luar cakupan datanya, dan petani dengan literasi digital rendah bisa salah membaca satuan. Pencegahannya sudah terpasang, yaitu penanda luar sebaran, label cakupan yang jelas (padi dan jagung, Bogor dan sekitarnya), dua tingkat satuan (kg/ha dan kg per petak), dan bahasa antarmuka Indonesia sederhana dengan ikon berlabel teks. Faktor modal petani tidak masuk fitur model sehingga rekomendasi bisa terasa berat bagi modal kecil, dan itu dijembatani paket hemat yang tetap dalam rentang aman.")

    h2("10.5 Kalibrasi kepercayaan")
    p("Antarmuka membantu pengguna menakar kepercayaan dengan empat cara, yaitu persentase keyakinan plus kata kategori berkode warna pada setiap hasil, penjelasan faktor dominan dalam kalimat sederhana, sub-label rentang aman resmi pada tiap kartu dosis sebagai pembanding, dan tombol kirim ke penyuluh yang selalu tersedia. Analisis kalibrasi di Bab 8.4 menunjukkan pita keyakinan tengah belum terkalibrasi baik, dan temuan itu justru memperkuat alasan desain kami untuk tetap menampilkan rentang aman dan anjuran verifikasi pada kategori Cukup yakin, bukan hanya pada kategori Tidak yakin.")

    daftar_periksa([
        ["Risiko memakai contoh konkret produk", "Terpenuhi (Tabel 10.1)"],
        ["Risiko tinggi punya mitigasi yang bisa ditunjukkan", "Terpenuhi, semuanya berupa elemen aplikasi nyata"],
        ["Teks disclaimer dan persetujuan ditulis lengkap", "Terpenuhi (10.2, 10.3)"],
        ["Guardrail diuji di Bab 8", "Terpenuhi (Tabel 10.2)"],
        ["Data sensitif dan minimisasinya dijelaskan", "Terpenuhi (Tabel 10.3)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 11 ADOPSI
# ======================================================================
def bab11():
    h1("Bab 11 Strategi Adopsi dan Rencana Lanjutan")

    h2("11.1 Mitra dan kanal")
    tabel("Tabel 11.1 Mitra potensial dan status kontaknya", ["Mitra", "Peran", "Status kontak", "Bukti"], [
        ["Poktan di wilayah Bogor (kandidat desa Cibinong dan sekitarnya)", "Lokasi pilot dan sumber data uji tanah", "Belum dihubungi", "Rencana kontak melalui penyuluh pembina saat persiapan pilot, jujur dicatat belum ada bukti kontak"],
        ["Penyuluh pertanian", "Verifikator rekomendasi dan kanal sosialisasi", "Belum dihubungi", "Menunggu arahan dosen untuk jalur kontak formal"],
        ["Kios saprodi lokal", "Kanal sosialisasi dan rujukan harga pupuk", "Belum dihubungi", "Harga rujukan sementara memakai asumsi HET di Bab 9"],
    ], lebar=[4.6, 4.0, 3.2, 4.2], ukuran=9.5)
    tabel(None, ["Kanal distribusi dan pelatihan", "Isi"], [
        ["Kanal", "Perkenalan lewat penyuluh saat kunjungan poktan, tautan aplikasi di grup WhatsApp poktan, brosur satu halaman di kios saprodi"],
        ["Pelatihan pengguna", "Sesi 30 menit di kumpulan poktan dengan ponsel petani langsung dipakai, bahasa Indonesia sederhana, fokus satu alur saja yaitu daftar lahan sampai hasil. Video panduan pendek direkam menjelang pilot"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("11.2 Tahapan rollout")
    tabel("Tabel 11.2 Tahapan rollout dan kriteria lanjut", ["Tahap", "Sasaran", "Jumlah pengguna", "Waktu", "Kriteria lanjut"], [
        ["Pilot", "Satu poktan di Bogor, dua komoditas", "Sekitar 25 petani", "Musim tanam hujan berikutnya", "Minimal 60 persen petani memakai kembali, kumpulan minimal 30 data uji tanah petani"],
        ["Perluasan", "Empat sampai lima poktan satu kecamatan", "Sekitar 100 petani", "Musim berikutnya setelah pilot", "Penghematan terukur minimal 10 persen tanpa penurunan hasil, model dilatih ulang dengan data lapangan"],
        ["Skala", "Perluasan wilayah dan komoditas, fitur rekap poktan", "Ratusan petani", "Setelah dua musim terukur", "Kesepakatan kemitraan dengan koperasi atau dinas"],
    ], lebar=[2.4, 4.6, 2.4, 2.8, 3.8], ukuran=9.5)

    h2("11.3 Umpan balik berkelanjutan")
    tabel(None, ["Aspek", "Isi"], [
        ["Cara pengguna melapor", "Status verifikasi penyuluh pada setiap hasil (setujui atau minta koreksi) menjadi saluran umpan balik pertama, ditambah wawancara singkat saat kunjungan poktan"],
        ["Siapa meninjau dan seberapa sering", "Tim meninjau catatan verifikasi tiap dua pekan selama pilot bersama penyuluh"],
        ["Pemanfaatan umpan balik", "Koreksi penyuluh dan selisih dosis yang dipakai petani menjadi data latih baru berlabel lapangan untuk pelatihan ulang musiman"],
    ], lebar=[3.6, 12.4], ukuran=10)

    h2("11.4 Roadmap")
    tabel("Tabel 11.3 Fitur yang ditunda beserta alasannya", ["Fitur ditunda dari MVP", "Alasan ditunda", "Prioritas", "Perkiraan waktu", "Ketergantungan"], [
        ["Draf RDKK otomatis kelompok", "Butuh akumulasi rekomendasi banyak petani yang baru ada setelah pilot", "Tinggi (kaitan langsung dengan model bisnis)", "Musim kedua", "Data anggota poktan aktif"],
        ["Data latih dari uji tanah dan catatan panen petani", "Butuh kerja sama lapangan", "Tinggi (paling menentukan mutu model)", "Sejak pilot", "Mitra poktan"],
        ["Kalender pemupukan pribadi", "Butuh data fase tanam per petak", "Sedang", "Musim kedua", "Riwayat petak cukup panjang"],
        ["Diagnosis hama dan penyakit dari foto", "Butuh dataset citra dan model visi, di luar jalur utama", "Sedang", "Tahun berikutnya", "Dataset foto lapangan"],
        ["Peta hara kolaboratif real-time", "Butuh banyak kontributor data dan tata kelola", "Rendah", "Setelah skala", "Jumlah pengguna besar"],
        ["Rilis APK Android (Flutter)", "Versi web cukup untuk pilot, Flutter direncanakan LKP-P6 untuk jangkauan pasang", "Sedang", "Setelah pilot stabil", "Konfirmasi alur dengan petani"],
    ], lebar=[4.2, 4.6, 2.4, 2.4, 2.4], ukuran=9)

    h2("11.5 Risiko adopsi")
    tabel("Tabel 11.4 Hambatan adopsi dan mitigasinya", ["Hambatan", "Bukti atau indikasi", "Mitigasi"], [
        ["Sinyal tidak stabil di lahan", "Asumsi profil petani (sinyal memadai di rumah dan kios)", "Hasil tersimpan lokal, pesan galat jelas, alur bisa diulang saat sinyal kembali"],
        ["Kepercayaan pada angka AI", "Umum pada produk AI untuk petani, dan terlihat pada persona", "Badge keyakinan jujur, rentang aman resmi selalu tampil, verifikasi penyuluh menjadi bagian alur bukan tambahan"],
        ["Beban mengisi data uji tanah", "Petani tidak punya angka lab", "Jalur peta hara tanpa angka, atau input kasar yang tetap dijaga guardrail"],
        ["Risiko aplikasi dianggap pengganti penyuluh", "Salah paham peran", "Pesan di Papan Penyuluhan dan disclaimer yang menegaskan verifikasi penyuluh"],
    ], lebar=[4.0, 5.0, 7.0], ukuran=9.5)

    daftar_periksa([
        ["Mitra dan kanal disertai bukti kontak", "Jujur belum ada bukti kontak, status tiap mitra tertulis eksplisit"],
        ["Pelatihan sesuai profil persona", "Terpenuhi (sesi singkat satu alur, bahasa sederhana)"],
        ["Mekanisme umpan balik ada di aplikasi", "Terpenuhi (panel verifikasi)"],
        ["Roadmap menjelaskan alasan setiap fitur ditunda", "Terpenuhi (Tabel 11.3)"],
    ])
    pecah_halaman()


# ======================================================================
# BAB 12 PENUTUP
# ======================================================================
def bab12():
    h1("Bab 12 Penutup")

    h2("12.1 Kesimpulan terhadap tujuan")
    tabel("Tabel 12.1 Tujuan Bab 1.3 dibanding capaian nyata", ["Tujuan (Bab 1.3)", "Target", "Capaian nyata", "Status", "Bukti"], [
        ["Angka dosis sejalan pakar", "Agreement 85 sampai 90 persen", "95,2 persen pada holdout", "Terlampaui", "Tabel 8.3"],
        ["Perhitungan cepat", "Kurang dari 5 detik", "p95 API 87 milidetik", "Terlampaui", "Tabel 8.3"],
        ["Keamanan keputusan", "0 keluaran luar rentang aman", "Seluruh uji guardrail lulus, kasus ragu tidak menampilkan angka", "Terpenuhi", "Tabel 8.3, Gambar 6.9"],
        ["Hasil bisa dipahami", "100 persen hasil dengan penjelasan dan keyakinan", "Seluruh jawaban memuat penjelasan dan keyakinan", "Terpenuhi", "Tabel 5.3"],
        ["Penghematan biaya petani", "Minimal 10 persen per musim", "Belum terukur, menunggu data pilot", "Belum", "Bab 11.2"],
    ], lebar=[3.6, 3.2, 4.4, 2.0, 2.8], ukuran=9.5)
    p("Kesimpulan umum: masalah yang kami rumuskan di Bab 1, yaitu petani tidak punya cara cepat, murah, dan aman untuk mengetahui dosis pupuk lahannya sendiri, telah dijawab oleh produk pada semua aspek yang bisa diuji tanpa data lapangan. Aspek yang butuh lapangan, yaitu penghematan nyata dan kepuasan petani, jujur kami laporkan belum terukur dan menjadi isi pilot.")

    h2("12.2 Keterbatasan dan saran")
    tabel(None, ["Aspek", "Isi"], [
        ["Keterbatasan produk", "Data latih adalah proxy dari logika tabel resmi sehingga keunggulan angka belum terbukti pada kondisi lapangan nyata. Komoditas terbatas padi dan jagung, wilayah menyasar Bogor. Nilai N-P-K dari peta memakai konversi band yang disederhanakan, bukan hasil uji lab per petak. Panel penyuluh dan riwayat berjalan lokal di perangkat, belum daring"],
        ["Keterbatasan proses", "Uji usability dilakukan terotomasi dan oleh anggota tim, bukan petani sasaran. Persona belum divalidasi wawancara. Mitra poktan belum dihubungi. Angka harga pupuk dan biaya server adalah asumsi yang ditandai jelas"],
        ["Saran perbaikan", "Jalankan pilot satu poktan sesuai Bab 11.2 untuk mengumpulkan data uji tanah dan catatan panen, lalu latih ulang model dan ukur ulang kalibrasi keyakinan pada data lapangan. Setelah itu migrasikan server ke FastAPI dengan kontrak yang sama dan rilis APK. Validasi persona lewat wawancara singkat saat sosialisasi pilot"],
    ], lebar=[3.2, 12.8], ukuran=10)

    h2("12.3 Kontribusi anggota")
    tabel("Tabel 12.2 Kontribusi anggota (total 100 persen)", ["Nama", "NIM", "Peran", "Bagian yang dikerjakan", "Bukti", "Persen"], [
        ["Irgi Setiawan", "M0405241018", "PIC model dan data", "Data proxy, pelatihan dan evaluasi model, konstanta guardrail, PoC, Bab 3 dan 4 laporan, koordinasi", "data_proxy.py, train.py, model.py, metrik_model.json, hasil_evaluasi_tambahan.json, poc/", "40"],
        ["Syarif Abdullah Assagaf", "M0405241033", "PIC server dan integrasi", "Server API, kontrak JSON, pengujian pytest 12 butir, pengukuran latensi, kalkulasi biaya Bab 9", "server.py, tests/test_api.py, konstanta.py", "30"],
        ["Thogianna Anggitouli Metanoia Sinaga", "M0405241077", "PIC antarmuka dan desain", "Wireframe LKP-P6, seluruh layar web, desain hi-fi SVG, tangkapan layar, Bab 6 laporan", "app/frontend/, docs/desain-figma/, docs/tangkapan-layar/, tests/perjalanan_ui.py", "30"],
    ], lebar=[3.4, 2.6, 2.6, 4.6, 2.6, 1.2], ukuran=9)
    p("Kami menyatakan isi laporan ini disetujui seluruh anggota kelompok. Bogor, 24 November 2026, Kelompok 14.")

    h2("12.4 Daftar periksa akhir sebelum dikumpulkan")
    daftar_periksa([
        ["Kotak petunjuk template, baris contoh, dan teks abu-abu sudah dihapus atau diganti", "Terpenuhi, seluruh isi diganti data kelompok"],
        ["Tautan halaman sampul bisa dibuka dari akun lain", "Terpenuhi untuk GitHub (publik) dan Figma, aplikasi demo berjalan lokal dengan petunjuk README"],
        ["Angka Ringkasan Eksekutif sama dengan angka bab terkait", "Terpenuhi (agreement, MAE, latensi, 12 pengujian, 18 langkah)"],
        ["ID fitur konsisten di Bab 5, 6, 7, dan 8", "Terpenuhi (F-01 sampai F-08, S-01 sampai S-07)"],
        ["Setiap gambar dan tabel bernomor, berjudul, dan dirujuk di teks", "Terpenuhi"],
        ["Daftar isi sudah diperbarui", "Terpenuhi (nomor halaman dari render final)"],
        ["Semua anggota membaca dan menyetujui laporan", "Terpenuhi (pernyataan di 12.3)"],
        ["Daftar pustaka memuat semua sumber yang dikutip", "Terpenuhi"],
    ])
    pecah_halaman()


# ======================================================================
# DAFTAR PUSTAKA
# ======================================================================
def pustaka():
    h1("Daftar Pustaka")
    daftar = [
        "Badan Pusat Statistik. Statistik Indonesia (berbagai tahun). Jakarta, BPS. Diakses sebagai rujukan profil wilayah.",
        "Kementerian Pertanian Republik Indonesia. Peraturan Menteri Pertanian Nomor 40/Pert/Hk.060/3/2007 tentang Anjuran Pemupukan Berimbang N, P, dan K pada Padi, Jagung, dan Kedelai. Jakarta.",
        "Lipenkova, J. (2025). The Art of AI Product Development: Delivering Business Value with Data, ML, and LLMs. Bahan perkuliahan PPKBP.",
        "Nika, M., dan Granados, R. The AI Product Playbook. Bahan perkuliahan PPKBP.",
        "Nika, M. The AI Product Development Lifecycle (AIPDL). Bahan Panduan Projek PPKBP.",
        "Pusat Penelitian dan Pengembangan Tanah dan Agroklimat (Balittanah). Kaidah interpretasi kesuburan tanah dan publikasi rekomendasi pemupukan spesifik lokasi. Bogor.",
        "Tim CAPS-32 Ilmu Komputer IPB. SAFRONS, Smart Agriculture and Fertilizer Recommendation System. https://safrons.vercel.app/. Diaudit pada LKP-P1.",
    ]
    for i, d in enumerate(daftar, 1):
        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        par.paragraph_format.line_spacing = 1.4
        run = par.add_run(f"{i}. {d}")
        run.font.size = Pt(12)
    pecah_halaman()


# ======================================================================
# LAMPIRAN
# ======================================================================
def lampiran():
    h1("Lampiran")

    h2("Lampiran A. AI PRD final")
    p("PRD final PupukPintar adalah gabungan Bab 5 (ruang lingkup, tabel 5.2 functional requirements dengan ID F-01 sampai F-09, tabel 5.3 NFR terukur, dan tabel 5.4 penelusuran fitur) plus catatan perubahan dari versi UTS pada Tabel 5.1. Tiga perubahan utama dari PRD v1.0 adalah penjelasan generatif menjadi templat rule-based demi akurasi dan biaya nol, sumber input peta berpindah dari rencana zona contoh ke peta spasial asli SAFRONS, dan server demo memakai pustaka standar Python dengan kontrak JSON yang identik rencana FastAPI. Seluruh field kontrak, ID fitur, dan NFR tidak berubah dari v1.0 sehingga penelusuran tetap satu garis.")

    h2("Lampiran B. Tautan")
    tabel(None, ["Item", "Tautan"], [
        ["Repositori GitHub", TAUTAN["github"]],
        ["Repositori PoC (LKP-P6)", TAUTAN["github_poc"]],
        ["Figma (wireframe)", TAUTAN["figma"]],
        ["Desain hi-fi SVG dan panduan", "docs/desain-figma/ pada repositori, berisi FIGMA_GUIDE.md"],
        ["Aplikasi demo", TAUTAN["app"]],
    ], lebar=[4.6, 11.4], ukuran=10)

    h2("Lampiran C. Panduan pelabelan dan data")
    p("Definisi kolom data latih (berkas app/backend/data_proxy.py): pH skala 3,8 sampai 8,2, N_persen 0,04 sampai 1,10, P_ppm (Bray-1) 2 sampai 120, K_me100g 0,04 sampai 1,20, tekstur salah satu dari Lempung, Lempung Liat, atau Liat, komoditas Padi atau Jagung, target hasil padi 4 sampai 8 t/ha dan jagung 4,5 sampai 10,5 t/ha, musim Hujan atau Kemarau.")
    p("Cara membaca label dosis dari tabel resmi: dosis dasar padi N 200, P 75, K 50 kg/ha dan jagung N 275, P 140, K 70 kg/ha pada kondisi tanah dan target sedang, dikoreksi proporsional terhadap status hara menurut batas kelas Balittanah (N 0,10, 0,21, 0,40, 0,60, P 5, 11, 26, 60, K 0,10, 0,21, 0,41, 0,80), ditambah efek target hasil, penyesuaian tanah masam (P naik 15 persen dan N naik 5 persen pada pH di bawah 5,5), faktor tekstur, dan tambahan N 5 persen musim hujan. Hasil akhir dikunci rentang aman Permentan (padi N 150-250, P 50-100, K 25-75, jagung N 200-350, P 100-200, K 40-100 kg/ha). Penanganan data kosong tidak diperlukan karena dataset dibangkitkan penuh, sedangkan aplikasi menolak input kosong dengan pesan per medan.")
    p("Penjaminan mutu: fungsi label deterministik dan diaudit terhadap rentang resmi, perubahan logika hanya lewat satu berkas sehingga jejaknya jelas pada riwayat git. Rencana mutu lanjutan: saat data lapangan masuk, sampel diberi label ganda oleh dua penilai dan tingkat kesepakatannya dihitung sebelum model dilatih ulang.")

    p("Pemetaan band SAFRONS ke nilai perwakilan skala model (peta wilayah):")
    tabel("Tabel C.1 Konversi band N-P-K peta SAFRONS ke nilai uji tanah model", ["Band SAFRONS", "Ambang pemisah band (nilai sumber)", "N (persen)", "P (ppm)", "K (me/100g)"], [
        ["Sangat rendah", "N di bawah 2,0, P di bawah 6,7, K di bawah 147,0", "0,07", "3,0", "0,06"],
        ["Rendah", "N di bawah 2,5, P di bawah 7,8, K di bawah 197,5", "0,15", "8,0", "0,15"],
        ["Sedang", "N di bawah 4,2, P di bawah 8,0, K di bawah 331,2", "0,30", "18,0", "0,30"],
        ["Tinggi", "N di bawah 5,5, P di bawah 9,0, K di bawah 447,9", "0,50", "40,0", "0,60"],
        ["Sangat tinggi", "nilai pada atau di atas ambang terakhir", "0,85", "90,0", "1,00"],
    ], lebar=[3.0, 6.6, 2.2, 2.2, 2.0], ukuran=9.5)
    p("Untuk petak yang digambar pengguna pada alat gambar (F-02), luas dihitung dari geometri gambaran memakai rumus luas poligon pada bola Chamberlain-Duquette dengan radius rata-rata 6.371.008,8 meter, kemudian nilai hara diambil dari unit SAFRONS tempat pusat petak berada (bila pusat jatuh di celah antar unit, dipakai unit terdekat menurut jarak titik ke titik terdekat unit). Geometri gambaran disimpan bersama lahan.")
    p("Nilai perwakilan dipilih agar status hara menurut batas kelas Balittanah yang kami pakai (Bab 3) jatuh pada kelas yang sama dengan band aslinya, sehingga rekomendasi dari peta konsisten dengan pembacaan SAFRONS. Area tanpa data (3 area) tidak dapat dipilih, meniru perilaku SAFRONS.")

    h2("Lampiran D. Hasil pengujian (data mentah)")
    p("Data mentah lengkap tersimpan di repositori dan dapat diulang siapa pun:")
    bullet("tests/test_api.py, 12 pengujian pytest (kontrak, guardrail 45 kombinasi ekstrem, luar sebaran, input buruk, determinisme, konversi dan biaya, paket, peringatan pH, model info dan peta, berkas statis, latensi p95). Hasil terakhir 12 lulus.")
    bullet("tests/perjalanan_ui.py, 20 langkah Playwright pada Chromium 390 piksel dengan pemeriksaan luapan horizontal, penggambaran petak, verifikasi ketepatan klik peta pada koordinat yang diketahui, dan perekaman galat konsol. Hasil terakhir 20 lulus tanpa galat konsol, tangkapan layarnya di docs/tangkapan-layar.")
    bullet("tests/hasil_evaluasi_tambahan.json, hasil baseline, kalibrasi keyakinan, dan contoh prediksi.")
    bullet("docs/perjalanan_ui_hasil.txt, catatan keluaran perjalanan UI.")
    p("Formulir umpan balik pengguna (untuk pilot, siap dipakai, skala 1 sangat tidak setuju sampai 5 sangat setuju):")
    tabel(None, ["Pernyataan", "1", "2", "3", "4", "5"], [
        ["Saya paham apa yang ditampilkan aplikasi", "", "", "", "", ""],
        ["Saya bisa menyelesaikan tugas tanpa bantuan", "", "", "", "", ""],
        ["Saya percaya pada hasil yang diberikan aplikasi", "", "", "", "", ""],
        ["Saya paham ketika aplikasi menyatakan tidak yakin", "", "", "", "", ""],
        ["Saya akan memakai aplikasi ini lagi", "", "", "", "", ""],
    ], lebar=[8.0, 1.4, 1.4, 1.4, 1.4, 1.4], ukuran=10)
    tabel(None, ["Pertanyaan terbuka", "Jawaban"], [
        ["Hal yang paling membantu", ""],
        ["Hal yang membingungkan atau salah", ""],
        ["Saran", ""],
    ], lebar=[6.0, 10.0], ukuran=10)

    h2("Lampiran E. LKP yang telah diisi")
    tabel(None, ["Lampiran", "Isi", "Ketentuan", "Sudah?"], [
        ["LKP-P1", "Audit produk SAFRONS", "Profil produk, deterministik vs probabilistik, anatomi, kelemahan dan usulan", "Ya, pada folder lkp1"],
        ["LKP-P2", "Pemilihan topik dan peluang AI", "Problem framing, AI Opportunity Tree, matriks prioritisasi, Lean Canvas", "Ya, pada folder lkp2"],
        ["LKP-P3", "Pemetaan solusi AI", "Modalitas data, pendekatan AI, UX dan otomasi, blueprint, keputusan GO", "Ya, pada folder lkp3"],
        ["LKP-P4", "Strategi data dan kelayakan", "Feature engineering, algoritma, pelabelan, metrik ML vs produk, time series, etika", "Ya, pada folder lkp4"],
        ["LKP-P5", "SRS, IA, dan sitemap", "Scope, requirements, halaman, sitemap", "Ya, pada folder lkp5"],
        ["LKP-P6", "Wireframe, PoC, blueprint teknis", "Wireframe 3 layar, PoC model, kontrak API, breakdown tugas", "Ya, pada folder lkp6 dan poc/ repositori"],
    ], lebar=[2.0, 5.0, 7.0, 2.0], ukuran=9.5)


# ======================================================================
# perakitan
# ======================================================================
def bangun():
    sampul()
    daftar_isi()
    ringkasan()
    bab1()
    bab2()
    bab3()
    bab4()
    bab5()
    bab6()
    bab7()
    bab8()
    bab9()
    bab10()
    bab11()
    bab12()
    pustaka()
    lampiran()


if __name__ == "__main__":
    bangun()
    keluar = os.path.join(REPO, "laporan", "Laporan_Akhir_PupukPintar_Kelompok14.docx")
    doc.save(keluar)
    print("tersimpan:", keluar)
