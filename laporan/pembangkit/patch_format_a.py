# -*- coding: utf-8 -*-
"""Patch format laporan: font 11/12/14, sampul baru, daftar isi bertitik,
daftar gambar dan daftar tabel, indentasi paragraf, daftar pustaka menggantung."""

p = "laporan/pembangkit/buat_laporan.py"
s = open(p, encoding="utf-8").read()

# ---------- 1) impor tambahan ----------
lama = "from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING"
baru = "from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER"
assert lama in s
s = s.replace(lama, baru)
lama = "import json\nimport os\nimport sys"
baru = "import json\nimport os\nimport re\nimport sys"
assert lama in s
s = s.replace(lama, baru)

# ---------- 2) gaya dasar: 11 isi, 12 subjudul, 14 judul, judul bab rata tengah ----------
lama = '''def atur_gaya():
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
        gaya.paragraph_format.line_spacing = 1.3'''
baru = '''def atur_gaya():
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    for nama, ukuran, sebelum in (("Heading 1", 14, 16), ("Heading 2", 12, 12), ("Heading 3", 12, 8)):
        gaya = doc.styles[nama]
        gaya.font.name = "Times New Roman"
        gaya.font.size = Pt(ukuran)
        gaya.font.bold = True
        gaya.font.color.rgb = RGBColor(0, 0, 0)
        gaya.paragraph_format.space_before = Pt(sebelum)
        gaya.paragraph_format.space_after = Pt(6)
        gaya.paragraph_format.line_spacing = 1.3
    doc.styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER'''
assert lama in s
s = s.replace(lama, baru)

# ---------- 3) p(): isi 11 dengan indentasi baris pertama ----------
lama = '''def p(isi, rata="justify", ukuran=12, sebelum=0, sesudah=6, miring=False, gaya=None):
    par = doc.add_paragraph(style=gaya)
    par.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "tengah": WD_ALIGN_PARAGRAPH.CENTER,
                     "kiri": WD_ALIGN_PARAGRAPH.LEFT, "kanan": WD_ALIGN_PARAGRAPH.RIGHT}[rata]
    par.paragraph_format.space_before = Pt(sebelum)
    par.paragraph_format.space_after = Pt(sesudah)
    run = par.add_run(isi)
    run.font.size = Pt(ukuran)
    run.italic = miring
    return par'''
baru = '''def p(isi, rata="justify", ukuran=11, sebelum=0, sesudah=6, miring=False, gaya=None):
    par = doc.add_paragraph(style=gaya)
    par.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "tengah": WD_ALIGN_PARAGRAPH.CENTER,
                     "kiri": WD_ALIGN_PARAGRAPH.LEFT, "kanan": WD_ALIGN_PARAGRAPH.RIGHT}[rata]
    par.paragraph_format.space_before = Pt(sebelum)
    par.paragraph_format.space_after = Pt(sesudah)
    if rata == "justify":
        par.paragraph_format.first_line_indent = Cm(1.0)
    run = par.add_run(isi)
    run.font.size = Pt(ukuran)
    run.italic = miring
    return par'''
assert lama in s
s = s.replace(lama, baru)

# ---------- 4) bullet 11 ----------
lama = "def bullet(isi, ukuran=12):"
baru = "def bullet(isi, ukuran=11):"
assert lama in s
s = s.replace(lama, baru)

# ---------- 5) h2: subjudul bernomor berakhiran titik ----------
lama = '''def h2(isi):
    par = doc.add_heading(isi, level=2)
    par.paragraph_format.keep_with_next = True'''
baru = '''def h2(isi):
    if re.match(r"^\\d+\\.\\d+ ", isi):
        isi = re.sub(r"^(\\d+\\.\\d+) ", r"\\1. ", isi)
    par = doc.add_heading(isi, level=2)
    par.paragraph_format.keep_with_next = True'''
assert lama in s
s = s.replace(lama, baru)

# ---------- 6) ganti sampul + daftar isi lama dengan sampul baru, TOC bertitik, ----------
#    daftar gambar, dan daftar tabel (isi mengikuti instruksi penugasan)
i_awal = s.index("def sampul():")
i_akhir = s.index("# ======================================================================\n# RINGKASAN EKSEKUTIF")
BLOK_BARU = r'''def sampul():
    def baris_sampul(teks, ukuran, tebal=False, sesudah=6):
        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(sesudah)
        par.paragraph_format.line_spacing = 1.3
        run = par.add_run(teks)
        run.font.size = Pt(ukuran)
        run.bold = tebal

    baris_sampul("LAPORAN PROYEK PPKBP", 14, True, 10)
    baris_sampul("Ditunjukkan untuk memenuhi tugas MK. Perancangan Produk Kecerdasan Buatan untuk Pertanian (KEB1322)", 12, False, 18)
    baris_sampul("Disusun Oleh Kelompok 14 | K1", 14, True, 8)
    baris_sampul("Irgi Setiawan - M0405241018", 12, False, 2)
    baris_sampul("Syarif Abdullah Assagaf - M0405241033", 12, False, 2)
    baris_sampul("Thogianna Anggitouli Metanoia Sinaga - M0405241077", 12, False, 20)
    par_logo = doc.add_paragraph()
    par_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par_logo.paragraph_format.space_after = Pt(20)
    par_logo.add_run().add_picture(os.path.join(REPO, "..", "proyek_akhir", "Logo-IPB-baru1000.png"), width=Cm(4.5))
    baris_sampul("PROGRAM STUDI KECERDASAN BUATAN", 14, True, 8)
    baris_sampul("SEKOLAH SAINS DATA MATEMATIKA DAN INFORMATIKA", 14, True, 8)
    baris_sampul("IPB UNIVERSITY", 14, True, 8)
    baris_sampul("BOGOR", 14, True, 8)
    baris_sampul("2026", 14, True, 0)
    pecah_halaman()


def judul_depan(teks):
    par = doc.add_heading(teks.upper(), level=1)
    par.paragraph_format.keep_with_next = True


def baris_daftar(nama, halaman, indent=0.0):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.line_spacing = 1.35
    pf.space_after = Pt(2)
    pf.left_indent = Cm(indent)
    pf.tab_stops.add_tab_stop(Cm(15.8), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    run = par.add_run(nama)
    run.font.size = Pt(11)
    run2 = par.add_run("\t" + str(halaman))
    run2.font.size = Pt(11)


def subbab_dari_sumber():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    judul = re.findall(r'h2\("(\d+\.\d+ [^"]+)"\)', src)
    return [re.sub(r"^(\d+\.\d+) ", r"\1. ", t) for t in judul]


def caption_dari_sumber(jenis):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    if jenis == "gambar":
        return re.findall(r'"((?:Gambar) \d+\.\d+ [^"]*)"', src)
    return re.findall(r'"((?:Tabel) [A-Z0-9]+\.\d+ [^"]*)"', src)


def daftar_isi():
    judul_depan("Daftar Isi")
    hal = HALAMAN_ISI

    def nomor(kunci):
        if not hal:
            return "..."
        return str(hal.get(kunci, "..."))

    baris_daftar("Daftar Isi", nomor("isi"))
    baris_daftar("Daftar Gambar", nomor("gambar"))
    baris_daftar("Daftar Tabel", nomor("tabel"))
    baris_daftar("Ringkasan Eksekutif", nomor("ringkasan"))
    sumber = open(os.path.abspath(__file__), encoding="utf-8").read()
    bab_list = re.findall(r'h1\("((?:Bab) \d+ [^"]+)"\)', sumber)
    sub_list = subbab_dari_sumber()
    for urut, bab_t in enumerate(bab_list, start=1):
        baris_daftar(bab_t, nomor("bab%d" % urut))
        for sub_t in sub_list:
            if sub_t.startswith("%d." % urut):
                baris_daftar(sub_t, nomor("sub_" + sub_t), indent=0.75)
    baris_daftar("Daftar Pustaka", nomor("pustaka"))
    baris_daftar("Lampiran", nomor("lampiran"))
    pecah_halaman()


def daftar_gambar():
    judul_depan("Daftar Gambar")
    hal = HALAMAN_ISI
    for cap in caption_dari_sumber("gambar"):
        kunci = "capg_" + cap
        baris_daftar(cap, str(hal.get(kunci, "...")) if hal else "...")
    pecah_halaman()


def daftar_tabel():
    judul_depan("Daftar Tabel")
    hal = HALAMAN_ISI
    for cap in caption_dari_sumber("tabel"):
        kunci = "capt_" + cap
        baris_daftar(cap, str(hal.get(kunci, "...")) if hal else "...")
    pecah_halaman()


'''
s = s[:i_awal] + BLOK_BARU + s[i_akhir:]

# ---------- 7) ringkasan memakai judul depan kapital ----------
lama = '''def ringkasan():
    h1("Ringkasan Eksekutif")'''
baru = '''def ringkasan():
    judul_depan("RINGKASAN EKSEKUTIF")'''
assert lama in s
s = s.replace(lama, baru)

# ---------- 8) daftar pustaka menggantung ala pedoman ----------
i_awal = s.index("def pustaka():")
i_akhir = s.index("# ======================================================================\n# LAMPIRAN")
PUSTAKA = r'''def pustaka():
    judul_depan("Daftar Pustaka")
    pustaka_daftar = [
        [("Badan Pusat Statistik. 2024. ", False), ("Statistik Indonesia 2024", True), (". Jakarta: Badan Pusat Statistik.", False)],
        [("Kementerian Pertanian Republik Indonesia. 2007. ", False), ("Peraturan Menteri Pertanian Nomor 40/Pert/Hk.060/3/2007 tentang Anjuran Pemupukan Berimbang N, P, dan K pada Padi, Jagung, dan Kedelai", True), (". Jakarta: Kementerian Pertanian Republik Indonesia.", False)],
        [("Lipenkova, Janna. 2025. ", False), ("The Art of AI Product Development: Delivering Business Value with Data, ML, and LLMs", True), (". Bahan ajar Perancangan Produk Kecerdasan Buatan untuk Pertanian, IPB University.", False)],
        [("Nika, Marcin dan Romain Granados. t.t. ", False), ("The AI Product Playbook", True), (". Bahan ajar Perancangan Produk Kecerdasan Buatan untuk Pertanian, IPB University.", False)],
        [("Nika, Marcin. t.t. ", False), ("The AI Product Development Lifecycle (AIPDL)", True), (". Bahan Panduan Projek PPKBP, IPB University.", False)],
        [("Pusat Penelitian dan Pengembangan Tanah dan Agroklimat (Balittanah). t.t. ", False), ("Kaidah Interpretasi Kesuburan Tanah dan Rekomendasi Pemupukan Spesifik Lokasi", True), (". Bogor: Balai Penelitian Tanah.", False)],
        [("Tim CAPS-32 Ilmu Komputer IPB. 2025. ", False), ("SAFRONS: Smart Agriculture and Fertilizer Recommendation System", True), (". https://safrons.vercel.app. Diakses 18 Agustus 2026.", False)],
    ]
    for entri in pustaka_daftar:
        par = doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.LEFT
        par.paragraph_format.line_spacing = 1.15
        par.paragraph_format.space_after = Pt(10)
        par.paragraph_format.left_indent = Cm(1.25)
        par.paragraph_format.first_line_indent = Cm(-1.25)
        for teks, miring in entri:
            run = par.add_run(teks)
            run.font.size = Pt(11)
            run.italic = miring


'''
s = s[:i_awal] + PUSTAKA + s[i_akhir:]

# ---------- 9) urutan perakitan ----------
lama = '''def bangun():
    sampul()
    daftar_isi()
    ringkasan()'''
baru = '''def bangun():
    sampul()
    daftar_isi()
    daftar_gambar()
    daftar_tabel()
    ringkasan()'''
assert lama in s
s = s.replace(lama, baru)

open(p, "w", encoding="utf-8").write(s)
print("patch format terpasang")
