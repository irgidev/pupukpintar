# -*- coding: utf-8 -*-
"""Pembangkit dua bahan pendukung presentasi:
1. Skrip_Presentasi_Kelompok14.pdf  (pembagian bicara per anggota)
2. Pengetahuan_Proyek_PupukPintar.pdf (bacaan lengkap untuk semua anggota)
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

DIR = os.path.dirname(os.path.abspath(__file__))

HIJAU = colors.HexColor("#1E5B3F")
HIJAU_TUA = colors.HexColor("#143D2B")
KUNING = colors.HexColor("#F9EED6")
GARIS = colors.HexColor("#DCE0D6")
ABU = colors.HexColor("#55635A")
LATAR = colors.HexColor("#F3F4EE")

LBAR, LTING = A4
MARGIN = 54


def gaya(ukuran=10.5, tebal=False, warna="#1D241F", rata=TA_JUSTIFY,
         sebelum=0, sesudah=6, leading=None):
    return ParagraphStyle(
        "g", fontName="Helvetica-Bold" if tebal else "Helvetica",
        fontSize=ukuran, leading=leading or (ukuran * 1.45), textColor=colors.HexColor(warna),
        alignment=rata, spaceBefore=sebelum, spaceAfter=sesudah)


G_JUDUL = gaya(19, True, "#143D2B", TA_LEFT, 0, 4, 24)
G_SUB = gaya(11.5, False, "#55635A", TA_LEFT, 0, 14)
G_H1 = gaya(14, True, "#1E5B3F", TA_LEFT, 16, 6)
G_H2 = gaya(11.5, True, "#143D2B", TA_LEFT, 10, 4)
G_H1.keepWithNext = 1
G_H2.keepWithNext = 1
G_ISI = gaya(10.5)
G_CATEK = gaya(9.5, False, "#55635A", TA_LEFT, 0, 4)
G_BICARA = gaya(10.5, False, "#1D241F", TA_JUSTIFY, 0, 7)
G_SERAH = gaya(10.5, True, "#7A5410", TA_LEFT, 2, 12)
G_SEL = gaya(9.5, False, "#1D241F", TA_LEFT, 0, 0, 13)
G_SEL_H = gaya(9.5, True, "#FFFFFF", TA_LEFT, 0, 0, 13)


def p(teks, g=G_ISI):
    return Paragraph(teks, g)


def h1(nomor, judul):
    return p("%s.  %s" % (nomor, judul), G_H1)


def tabel(judul, kepala, baris, lebar):
    data = [[Paragraph(k, G_SEL_H) for k in kepala]]
    for b in baris:
        data.append([Paragraph(str(x), G_SEL) for x in b])
    t = Table(data, colWidths=lebar, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HIJAU),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LATAR]),
        ("GRID", (0, 0), (-1, -1), 0.6, GARIS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    hasil = []
    if judul:
        cap = gaya(9.5, True, "#55635A", TA_LEFT, 8, 3)
        cap.keepWithNext = 1
        hasil.append(Paragraph(judul, cap))
    hasil.append(t)
    hasil.append(Spacer(1, 6))
    return hasil


def dengan_nomor(jalur, judul_kaki):
    def kaki(kanvas, dok):
        kanvas.saveState()
        kanvas.setFont("Helvetica", 8.5)
        kanvas.setFillColor(ABU)
        kanvas.drawString(MARGIN, 30, judul_kaki)
        kanvas.drawRightString(LBAR - MARGIN, 30, "halaman %d" % dok.page)
        kanvas.setStrokeColor(GARIS)
        kanvas.setLineWidth(0.6)
        kanvas.line(MARGIN, 42, LBAR - MARGIN, 42)
        kanvas.restoreState()

    dok = BaseDocTemplate(jalur, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=54, bottomMargin=56)
    bingkai = Frame(MARGIN, 56, LBAR - 2 * MARGIN, LTING - 110, id="utama")
    dok.addPageTemplates([PageTemplate(id="hal", frames=[bingkai], onPage=kaki)])
    return dok


# =====================================================================
# DOKUMEN 1: SKRIP PRESENTASI
# =====================================================================

SLIDE_SKRIP = [
    ("IRGI SETIAWAN  ·  SLIDE 1 SAMPAI 4", [
        ("Slide 1  ·  Sampul dan ajakan coba sendiri  (sekitar 60 detik)", [
            "Assalamualaikum warahmatullahi wabarakatuh, selamat pagi Bapak, Ibu, dan teman-teman sekalian. "
            "Kami dari Kelompok 14. Saya Irgi Setiawan, bersama Syarif Abdullah Assagaf dan Thogianna Sinaga. "
            "Pada mata kuliah PPKBP kami membangun PupukPintar, sebuah aplikasi yang membantu petani padi dan "
            "jagung mengetahui dosis pupuk N-P-K yang tepat untuk lahannya sendiri, bukan menebak dari kebiasaan tetangga.",
            "Aplikasi ini sudah tayang dan bisa dicoba langsung hari ini di alamat pupukpintar.vercel.app. "
            "Di layar ada juga tautan kode sumber di GitHub, desain antarmuka di Figma, dan video demo di Google Drive. "
            "Kami sangat mengundang Bapak Ibu mencoba sendiri setelah sesi ini.",
            "Alur presentasi kami begini. Saya akan membuka dengan masalah, solusi AI, dan demo singkat. "
            "Selanjutnya Syarif menjelaskan pengujian dan sisi ekonominya. Terakhir Anggi menutup dengan tata kelola "
            "serta rencana ke depan. Kita mulai dari masalahnya.",
        ]),
        ("Slide 2  ·  Masalah dan pengguna  (sekitar 75 detik)", [
            "Masalahnya sederhana, tetapi akibatnya mahal. Petani padi dan jagung skala kecil di Bogor memupuk "
            "dengan meniru petak tetangganya, padahal kondisi hara tanah antarpetak berbeda. Uji tanah laboratorium "
            "memang bisa menjawab, tetapi biayanya sekitar seratus lima puluh ribu rupiah per sampel, ini asumsi tim "
            "yang akan kami konfirmasi saat pilot, dan prosedurnya dianggap ribet. Akibatnya dosis sering salah, "
            "biaya membengkak, dan hasil panen tidak optimal.",
            "Kami merumuskannya dalam satu kalimat di layar: petani membutuhkan cara cepat, murah, dan mudah untuk "
            "mengetahui dosis yang tepat untuk lahannya sendiri.",
            "Pengguna yang kami wujudkan menjadi persona adalah Pak Wandi, empat puluh satu tahun, petani padi dan "
            "jagung anggota kelompok petani di Cibinong dengan lahan setengah sampai satu hektar. Tujuannya menekan "
            "biaya pupuk tanpa menurunkan hasil. Kendalanya kebiasaan meniru tetangga dan anggapan uji lab mahal. "
            "Perangkatnya Android biasa dengan kuota terbatas, jadi aplikasi wajib ringan.",
            "Satu temuan yang mendorong kami maju: saat mengaudit peta hara SAFRONS, aplikasi peta hara yang kami "
            "audit sama sekali tidak mengeluarkan angka dosis, nol dosis. Artinya ada ruang nyata untuk produk yang "
            "memberi angka yang aman dan bisa dipertanggungjawabkan.",
            "Dari masalah ini kami merancang solusi AI-nya, yang masih saya jelaskan di slide berikutnya.",
        ]),
        ("Slide 3  ·  Solusi dan pendekatan AI  (sekitar 70 detik)", [
            "PupukPintar bekerja dalam empat bagian yang ada di diagram. Input-nya kondisi lahan: pH, unsur N, P, K, "
            "tekstur tanah, komoditas, target hasil, luas petak, dan musim. Petani bisa mengambil data ini dengan "
            "memilih unit lahannya di peta hara, atau memasukkan hasil uji tanah kalau punya.",
            "Otaknya model Random Forest Regressor dengan tiga ratus pohon. Model memprediksi tiga angka sekaligus, "
            "yaitu dosis N, P, dan K dalam kilogram per hektar. Di sekelilingnya ada dua lapis pengaman: perhitungan "
            "keyakinan dari sebaran jawaban antarpohon, dan guardrail yang mengunci keluaran ke rentang resmi "
            "Permentan nomor 40 tahun 2007 plus kaidah interpretasi Balittanah.",
            "Yang diterima petani di layar adalah kartu dosis, kebutuhan pupuk dan estimasi biaya dalam rupiah, tiga "
            "paket sesuai modal, serta penjelasan dengan bahasa sederhana. Nilainya jelas: dosis tepat per lahan, "
            "potensi hemat biaya, dan keputusan tetap aman karena lewat verifikasi penyuluh.",
            "Soal pendekatan AI kami jujur di layar: kami memakai pendekatan predictive sebagai inti regresi dan "
            "rule-based sebagai pengaman. Penjelasan memakai templat, bukan model generatif, supaya tidak ada risiko "
            "angka dikarang. Pendekatan agentic kami tunda sampai ada data lapangan.",
            "Sekarang bagian paling menyenangkan, demonya, slide empat.",
        ]),
        ("Slide 4  ·  Demo produk  (sekitar 75 detik)", [
            "Demo berjalan dalam tiga langkah. Pertama, petani mencari daerahnya dengan pencarian, memilih unit "
            "lahannya di peta, dan peta otomatis membesarkan unit yang dipilih. Kalau punya hasil uji tanah, jalur "
            "itu juga tersedia. Setelah itu pilih komoditas dan target hasil.",
            "Kedua, AI memproses. Random Forest memprediksi dosis N-P-K, keyakinan dihitung dari sebaran jawaban "
            "antarpohon, dan guardrail mengunci rentang aman. Semua selesai di bawah seratus milidetik, persentil "
            "sembilan puluh lima API kami delapan puluh tujuh milidetik.",
            "Ketiga, pengguna menerima hasil lengkap: dosis per hektar dan per petak, estimasi biaya, tiga paket "
            "modal, badge keyakinan, penjelasan, dan disclaimer. Untuk lahan demo kami, padi nol koma tujuh lima "
            "hektar, keyakinannya delapan puluh satu persen dengan kategori cukup yakin.",
            "Kami menyiapkan rencana cadangan. Kalau demo langsung terhalang jaringan, kami memutar video demo di "
            "Google Drive yang tautannya ada di sampul dan penutup. Data demo juga kami kunci agar hasilnya pasti "
            "sama: padi, pH lima koma empat, target enam ton per hektar.",
            "Demikian bagian saya. Selanjutnya Syarif akan menjelaskan bagaimana kami menangani ketidakpastian AI "
            "dan membuktikan kualitasnya. Silakan Syarif.",
        ]),
    ]),
    ("SYARIF ABDULLAH ASSAGAF  ·  SLIDE 5 SAMPAI 7", [
        ("Slide 5  ·  AI UX dan ketidakpastian  (sekitar 70 detik)", [
            "Terima kasih, Irgi. Saya Syarif akan menjelaskan bagaimana PupukPintar bersikap jujur ketika modelnya "
            "ragu. Kami membagi keluaran model menjadi tiga kategori berkode warna.",
            "Kategori pertama, yakin, yaitu keyakinan delapan puluh lima persen ke atas, badge hijau. Contohnya "
            "keyakinan sembilan puluh lima persen. Kartu dosis tampil lengkap dengan sub-label rentang aman resmi "
            "di bawah setiap angka, tetap disertai disclaimer dan tombol verifikasi penyuluh.",
            "Kategori kedua, ragu, yaitu keyakinan tujuh puluh sampai delapan puluh lima persen, badge kuning. "
            "Angka tetap tampil tetapi selalu dengan rentang aman, dan anjuran cek ulang serta verifikasi diperkuat. "
            "Contoh nyatanya tadi di demo Irgi: delapan puluh satu persen, kategori cukup yakin.",
            "Kategori ketiga, kondisi masukan di luar sebaran data latih, badge merah. Di sini kami tidak menampilkan "
            "angka sama sekali, karena memberi angka di luar wilayah data sama dengan tebak-tebakan. Petani "
            "diarahkan ke uji tanah laboratorium atau penyuluh.",
            "Semua ini bagian dari prinsip human-in-the-loop. Keputusan menjalankan pemupukan tetap di tangan petani "
            "setelah verifikasi penyuluh, melalui tombol Kirim ke Penyuluh pada setiap hasil dan panel verifikasi "
            "pada Papan Penyuluhan. Lalu apakah kualitasnya terbukti? Jawabannya ada di slide enam.",
        ]),
        ("Slide 6  ·  Hasil pengujian  (sekitar 85 detik)", [
            "Kami mengukur kualitas lewat lima dimensi Minimum Viable Quality yang ada di tabel.",
            "Pertama, agreement dengan rekomendasi resmi mencapai sembilan puluh lima koma dua persen pada seribu "
            "dua ratus baris data uji yang benar-benar terpisah, di atas ambang delapan puluh lima sampai sembilan "
            "puluh persen. Kedua, waktu respons, persentil sembilan puluh lima hanya delapan puluh tujuh milidetik "
            "dari tiga puluh permintaan, jauh di bawah target lima detik. Ketiga, guardrail rentang aman diuji dengan "
            "empat puluh lima kombinasi input ekstrem, semua keluaran tetap terkunci di rentang resmi, nol pelanggaran. "
            "Keempat, explainability, seratus persen hasil menyertakan penjelasan dan keyakinan. Kelima, keamanan kasus "
            "ragu, seratus persen kasus di luar sebaran berakhir tanpa angka dan diarahkan ke jalur aman.",
            "Uji antarmuka kami sebanyak dua puluh langkah otomatis, semuanya lulus tanpa galat konsol.",
            "Kami juga terbuka soal temuan. Keyakinan pita tengah belum terkalibrasi bagus: kelompok cukup yakin hanya "
            "mencapai agreement empat puluh dua koma sembilan persen, meski kasusnya jarang, hanya satu koma dua persen. "
            "Perbaikannya, kategori ini selalu disertai rentang aman dan anjuran verifikasi. Badge keyakinan pernah "
            "terpotong di layar tiga ratus sembilan puluh piksel dan sudah kami pindahkan ke baris sendiri. Data uji "
            "kami pisahkan dari data latih dengan seed berbeda sejak awal, jadi tidak pernah disentuh saat pemilihan model.",
            "Satu dimensi yang belum tercapai jujur kami sebut: kepuasan petani belum diukur karena pilot belum jalan. "
            "Lalu berapa biayanya? Ada di slide tujuh.",
        ]),
        ("Slide 7  ·  Ekonomi AI dan model bisnis  (sekitar 75 detik)", [
            "PupukPintar tidak memakai LLM, jadi tidak ada biaya token. Biaya per prediksi kami hitung dari biaya "
            "server per bulan dibagi jumlah prediksi per bulan, dengan asumsi VPS satu CPU satu gigabyte sembilan "
            "puluh ribu rupiah per bulan.",
            "Hasilnya tiga skenario di tabel. Satu poktan dengan dua puluh lima petani, sekitar seratus dua puluh lima "
            "prediksi per bulan, biayanya tujuh ratus dua puluh rupiah per prediksi. Empat poktan seratus petani, "
            "seratus delapan puluh rupiah. Dua puluh poktan lima ratus petani, tujuh puluh dua rupiah. Sebagai "
            "pembanding, satu uji tanah laboratorium sekitar seratus lima puluh ribu rupiah, setara dua ratus delapan "
            "prediksi di skenario paling konservatif.",
            "Cara kami menekan biaya: tiga ratus pohon tanpa GPU, penjelasan dari templat tanpa LLM, dan data peta "
            "yang statis.",
            "Model bisnisnya begini: pilot gratis. Kelak poktan atau koperasi berlangganan dengan iuran sekitar dua "
            "puluh lima ribu rupiah per bulan untuk rekap kebutuhan anggota. Titik impasnya empat poktan. Kami jujur "
            "menandai bukti kesediaan bayar sebagai asumsi untuk divalidasi saat pilot, belum ada tagihan nyata. "
            "Selain server, pelatihan ulang model tiap musim hanya empat detik di laptop tanpa GPU, dan domain sekitar "
            "dua ratus ribu rupiah per tahun.",
            "Selanjutnya Anggi akan menjelaskan sisi tata kelola, keamanan, dan rencana ke depan. Silakan Anggi.",
        ]),
    ]),
    ("THOGIANNA (ANGGI) SINAGA  ·  SLIDE 8 SAMPAI 10", [
        ("Slide 8  ·  Governance dan keamanan  (sekitar 75 detik)", [
            "Terima kasih, Syarif. Saya Anggi akan menjelaskan bagaimana kami menjaga produk tetap aman dan "
            "bertanggung jawab.",
            "Kami memetakan tiga risiko utama. Pertama, prediksi keliru di luar sebaran data latih, peluangnya sedang "
            "dan dampaknya tinggi. Mitigasinya terpasang dan teruji: guardrail rentang resmi, penanda luar sebaran, "
            "dan angka yang disembunyikan. Kedua, ketergantungan berlebih pada AI. Mitigasinya badge keyakinan, kata "
            "kategori, disclaimer permanen, dan jalur penyuluh. Ketiga, salah paham satuan. Layar hasil menampilkan "
            "kilogram per hektar dan kilogram per petak sekaligus dengan luas yang tertulis.",
            "Ada enam guardrail yang terpasang dan diuji: kunci rentang Permentan, penolakan input buruk, penanda "
            "luar sebaran, ambang keyakinan nol koma tujuh nol, peringatan Balittanah seperti pengapuran di tanah "
            "masam dan urea dibagi dua tahap saat musim hujan, serta disclaimer permanen. Teksnya persis seperti di "
            "layar: rekomendasi awal dari model, bukan pengganti uji tanah laboratorium, verifikasi penyuluh sebelum "
            "pembelian pupuk.",
            "Soal privasi, data lahan disimpan di perangkat petani sendiri melalui localStorage, tidak ada server "
            "yang menyimpan koordinat. Persetujuan diambil saat onboarding dengan kalimat yang tertera di layar. Di "
            "halaman Profil ada saklar tolak pelatihan model dan tombol hapus semua data, jadi pengguna benar-benar "
            "bisa pergi sambil membawa datanya.",
            "Lalu bagaimana produk ini sampai ke tangan petani? Ada di slide sembilan.",
        ]),
        ("Slide 9  ·  Adopsi dan rencana lanjutan  (sekitar 75 detik)", [
            "Rencana keberangkatan kami tiga tahap. Tahap pilot: satu poktan di Bogor, sekitar dua puluh lima petani, "
            "pada musim hujan berikutnya. Tahap perluasan: empat sampai lima poktan, sekitar seratus petani, model "
            "dilatih ulang dengan data lapangan hasil pilot. Tahap skala: kerja sama koperasi atau dinas dengan "
            "perluasan wilayah dan komoditas.",
            "Kami juga jujur menunda beberapa fitur dan menyebut alasannya. Draf RDKK otomatis menunggu akumulasi "
            "data anggota yang baru ada setelah pilot. Kalender pemupukan pribadi menunggu riwayat petak lintas musim. "
            "Diagnosis hama dari foto butuh dataset citra dan model visi yang terpisah. Rilis APK Android menunggu "
            "alur yang sudah terkonfirmasi petani.",
            "Keterbatasan kami kami nyatakan terbuka. Data latih masih proxy tabel resmi dan validasi lapangan belum "
            "selesai. Penguji usability masih tim sendiri, petani sasaran menyusul di pilot. Pelajaran terpenting "
            "kami: model yang bagus pada data proxy belum berarti benar di lapangan, karena itu guardrail dan jalur "
            "manusia kami rancang sejak hari pertama, bukan ditempel belakangan. Umpan balik berjalan lewat panel "
            "verifikasi penyuluh dan kunjungan poktan tiap dua pekan.",
            "Terakhir, mari kita rangkum semuanya di slide sepuluh.",
        ]),
        ("Slide 10  ·  Ringkasan dan penutup  (sekitar 60 detik)", [
            "Satu produk, empat kriteria. Functionality and AI Integration: agreement sembilan puluh lima koma dua "
            "persen pada data uji terpisah, latensi delapan puluh tujuh milidetik, guardrail rentang resmi lulus "
            "seluruh uji. AI UX and Uncertainty Handling: tiga kategori keyakinan berkode warna, kasus ragu dan luar "
            "sebaran tidak pernah menampilkan angka. Business Viability: seratus delapan puluh rupiah per prediksi "
            "pada skenario realistis tanpa biaya token, titik impas empat poktan. Governance and Safety: enam "
            "guardrail teruji, persetujuan dan penghapusan data ada di aplikasi, keputusan akhir tetap pada manusia.",
            "Semuanya bisa dibuktikan sendiri. Aplikasinya di pupukpintar.vercel.app, kode sumber di GitHub, desain "
            "di Figma, dan video demo di Google Drive. Tautannya ada di layar.",
            "Demikian presentasi dari Kelompok 14. Terima kasih atas waktu dan perhatian Bapak Ibu. Kami membuka "
            "sesi tanya jawab.",
        ]),
    ]),
]

PENYELAMAT = [
    ("Kalau demo langsung gagal karena jaringan",
     "Karena jaringan bisa tidak menentu, kami menyiapkan video demo di Google Drive yang tautannya ada di sampul. "
     "Izinkan kami memutarnya sekarang."),
    ("Kalau ditanya di luar cakupan proyek",
     "Pertanyaan bagus. Itu masuk wilayah yang belum kami kerjakan dan sudah kami catat untuk tahap pilot. "
     "Dengan senang hati kami diskusikan lebih detail di sesi tanya jawab."),
    ("Kalau ditanya kenapa tidak pakai ChatGPT atau LLM",
     "Target kami berupa angka dosis yang wajib akurat dan patuh rekomendasi resmi. Regresi dengan guardrail lebih "
     "cocok dan biayanya nol token, sedangkan model bahasa berisiko mengarang angka."),
    ("Kalau lupa angka saat bicara",
     "Cukup arahkan ke layar dan sebut yang tertera: agreement sembilan puluh lima koma dua persen, latensi delapan "
     "puluh tujuh milidetik, dua puluh langkah uji lulus. Semua angka kunci ada di slide."),
]


def bangun_skrip():
    dok = dengan_nomor(os.path.join(DIR, "Skrip_Presentasi_Kelompok14.pdf"),
                       "Skrip Presentasi PupukPintar · Kelompok 14 · PPKBP")
    cerita = []
    cerita.append(p("SKRIP PRESENTASI PupukPintar", G_JUDUL))
    cerita.append(p("Grand Demo Day KEB1322 · PPKBP · Kelompok 14 · IPB University", G_SUB))
    cerita.append(p(
        "Pembagian bicara: Irgi Setiawan membuka dan menjelaskan slide 1 sampai 4, Syarif Abdullah Assagaf "
        "menjelaskan slide 5 sampai 7, dan Thogianna (Anggi) Sinaga menjelaskan slide 8 sampai 10. Total durasi "
        "bicara sekitar sembilan sampai sepuluh menit tanpa demo langsung, atau tambah dua sampai tiga menit "
        "bila demo dibuka."))
    cerita.extend(tabel(
        "PEMBAGIAN SEKILAS",
        ["Pembicara", "Slide", "Isi pokok", "Durasi"],
        [["Irgi Setiawan", "1 - 4", "Pembukaan, masalah dan pengguna, solusi AI, demo", "sekitar 4,5 menit"],
         ["Syarif Abdullah Assagaf", "5 - 7", "Ketidakpastian AI, hasil pengujian, ekonomi AI", "sekitar 3,5 menit"],
         ["Thogianna (Anggi) Sinaga", "8 - 10", "Tata kelola dan keamanan, adopsi, ringkasan dan penutup", "sekitar 3,5 menit"]],
        [110, 45, 215, 80]))
    cerita.append(p("Cara memakai skrip ini", G_H2))
    cerita.append(p(
        "Baca keras dua kali sambil berdiri, lalu latih serah terima antarpembicara minimal sekali supaya peralihan "
        "tidak jeda. Tidak perlu menghafal kata per kata, cukup paham alurnya: setiap slide punya satu ide besar, "
        "dan kalimat terakhir tiap bagian sudah menjadi jembatan ke pembicara berikutnya. Saat menyebut angka, "
        "tunjuk bagian slide yang bersangkutan. Berbicara santai, tarik napas di akhir tiap paragraf."))
    for bagian, slide_blok in SLIDE_SKRIP:
        cerita.append(p(bagian, gaya(13, True, "#FFFFFF", TA_LEFT, 14, 0, 18)))
        cerita.append(Spacer(1, 6))
        for judul_slide, paragraf in slide_blok:
            cerita.append(p(judul_slide, G_H1))
            for teks in paragraf:
                cerita.append(p(teks, G_BICARA))
    cerita.append(h1("A", "Kalimat penyelamat untuk situasi sulit"))
    for situasi, kalimat in PENYELAMAT:
        cerita.append(p(situasi, G_H2))
        cerita.append(p(kalimat, G_BICARA))
    dok.build(cerita)
    print("selesai:", dok.filename)


# =====================================================================
# DOKUMEN 2: PENGETAHUAN PROYEK LENGKAP
# =====================================================================

def bangun_pengetahuan():
    dok = dengan_nomor(os.path.join(DIR, "Pengetahuan_Proyek_PupukPintar.pdf"),
                       "Pengetahuan Proyek PupukPintar · Kelompok 14 · PPKBP")
    c = []

    def bagian(nomor, judul):
        c.append(h1(nomor, judul))

    def sub(judul):
        c.append(p(judul, G_H2))

    # ---- sampul ringkas
    c.append(p("PENGETAHUAN PROYEK PupukPintar", G_JUDUL))
    c.append(p("Bacaan lengkap untuk seluruh anggota Kelompok 14 · KEB1322 PPKBP · IPB University", G_SUB))
    c.append(p(
        "Dokumen ini merangkum seluruh isi proyek agar setiap anggota memahami gambaran besar sampai detail "
        "teknis, termasuk hal yang tidak dibawakan pada slide. Bahasanya disederhanakan untuk dibaca cepat, "
        "tetapi angka dan istilahnya sama dengan laporan akhir dan PPT, jadi aman dikutip saat tanya jawab."))

    bagian(1, "Identitas dan ringkasan satu halaman")
    c.extend(tabel(None, ["Butir", "Isi"], [
        ["Nama proyek", "PupukPintar"],
        ["Mata kuliah", "KEB1322 Perancangan Produk Kecerdasan Buatan untuk Pertanian (PPKBP)"],
        ["Kelompok", "Kelompok 14, K1, Ilmu Komputer IPB University, Semester Ganjil 2026/2027"],
        ["Anggota", "Irgi Setiawan (M0405241018), Syarif Abdullah Assagaf (M0405241033), "
                    "Thogianna A. M. Sinaga (M0405241077)"],
        ["Masalah", "Petani padi dan jagung kecil di Bogor memupuk dengan meniru tetangga karena uji tanah "
                    "laboratorium sulit dijangkau, sehingga dosis salah dan biaya membengkak"],
        ["Solusi", "Aplikasi web yang memberi dosis pupuk N-P-K spesifik per lahan dengan model Random Forest, "
                    "guardrail rentang resmi, badge keyakinan, estimasi biaya, dan verifikasi penyuluh"],
        ["Angka kunci", "Agreement 95,2 persen pada 1.200 baris uji terpisah, latensi p95 87 ms, 12 pengujian API "
                        "dan 20 langkah uji antarmuka lulus, biaya 180 rupiah per prediksi pada skenario realistis"],
        ["Status", "Prototipe produksi tayang dan teruji, pilot poktan direncanakan musim hujan berikutnya"],
        ["Tautan", "Aplikasi pupukpintar.vercel.app, kode github.com/irgidev/pupukpintar, desain dan video demo "
                    "tautannya ada di sampul PPT"],
    ], [95, 355]))

    bagian(2, "Masalah dan pengguna")
    c.append(p(
        "Dosis pupuk yang salah punya dua wajah. Kalau terlalu sedikit, hasil panen turun. Kalau berlebihan, biaya "
        "membengkak dan hara berlebih mencemari. Petani kecil di Bogor umumnya memupuk mengikuti kebiasaan tetangga "
        "atau kebiasaan musim lalu, padahal pH dan stok N, P, K antarpetak bisa sangat berbeda. Jalur resmi untuk "
        "menjawabnya adalah uji tanah laboratorium, tetapi biayanya diperkirakan sekitar Rp 150.000 per sampel "
        "(asumsi tim, dikonfirmasi saat pilot) dan prosedurnya dianggap ribet, sehingga jarang dipakai petani kecil."))
    c.append(p(
        "Temuan audit LKP-P1 kami memperkuat: aplikasi peta hara yang kami audit mengeluarkan nol angka dosis. "
        "Peta hanya menunjukkan wilayah, tidak menjawab berapa kilogram pupuk yang harus dibeli. Di situlah PupukPintar "
        "mengisi kekosongan: dari kondisi lahan menuju angka dosis yang aman."))
    c.append(p(
        "Pengguna utama diwakili persona Pak Wandi, 41 tahun, petani padi dan jagung anggota poktan di Cibinong, "
        "lahan 0,5 sampai 1 ha, tujuan menekan biaya pupuk tanpa menurunkan hasil, perangkat Android biasa dengan "
        "kuota terbatas. Persona ini kandidat, dan akan divalidasi saat pilot. Pengguna kedua adalah penyuluh yang "
        "memverifikasi hasil sebelum dipakai."))
    sub("Konsekuensi desain dari profil pengguna")
    c.append(p(
        "Tiga keputusan desain lahir dari persona ini. Pertama, aplikasi wajib ringan dan tetap terpakai saat sinyal "
        "lemah, sehingga peta memakai kanvas vektor mandiri tanpa tile peta daring. Kedua, angka harus bisa dipahami "
        "tanpa istilah teknis, sehingga tiap hasil disertai penjelasan sederhana. Ketiga, keputusan akhir tetap pada "
        "manusia, sehingga tombol kirim ke penyuluh ada di setiap hasil."))

    bagian(3, "Basis ilmiah dan aturan resmi")
    c.append(p(
        "Seluruh angka dalam aplikasi berakar pada dua sumber resmi. Pertama, Permentan No. 40/2007 tentang "
        "rekomendasi dosis pupuk N, P, dan K untuk padi dan jagung berdasarkan target hasil dan musim. Kedua, kaidah "
        "interpretasi kesuburan tanah Balittanah yang memetakan nilai pH, N, P, K menjadi status Sangat Rendah sampai "
        "Tinggi, sekaligus memicu peringatan seperti pengapuran pada tanah masam dan pembagian urea dua tahap pada "
        "musim hujan."))
    c.extend(tabel(
        "Rentang aman dosis yang mengunci keluaran model (kg/ha), sumber Permentan 40/2007",
        ["Komoditas", "N min", "N maks", "P min", "P maks", "K min", "K maks"],
        [["Padi", "150", "250", "50", "100", "25", "75"],
         ["Jagung", "200", "350", "100", "200", "40", "100"]],
        [96, 60, 64, 60, 64, 60, 64]))
    c.append(p(
        "Peta lahan memakai 191 unit lanskap hara SAFRONS wilayah Bogor yang berisi perkiraan pH dan status N, P, K "
        "per unit. Koordinat aslinya dalam sistem UTM zona 48S lalu dikonversi ke lintang-bujur WGS84 supaya bisa "
        "digambar di kanvas aplikasi."))
    sub("Pemetaan unsur ke pupuk niaga dan harga")
    c.extend(tabel(None, ["Unsur", "Pupuk niaga", "Harga acuan (Rp/kg)", "Kadar unsur"],
                   [["N", "Urea", "2.250", "46 persen N"],
                    ["P", "SP-36", "2.300", "kadar P2O5 seperti konstanta aplikasi"],
                    ["K", "KCl", "5.000", "kadar K2O seperti konstanta aplikasi"]],
                   [60, 80, 105, 205]))
    c.append(p(
        "Dosis unsur dikonversi menjadi kebutuhan pupuk niaga per petak dengan memperhitungkan kadar unsur, lalu "
        "dikalikan harga acuan untuk estimasi biaya. Harga adalah asumsi harga kios dan bisa diubah di satu tempat "
        "yaitu konstanta aplikasi."))

    bagian(4, "Data latih dan cara pembangkitannya")
    c.append(p(
        "Model dilatih dari 6.000 baris data proxy. Disebut proxy karena barisnya bukan hasil uji laboratorium, "
        "melainkan hasil ekstraksi tabel resmi Permentan 40/2007 yang diberi label dosis pakar, dipadukan dengan "
        "kaidah Balittanah untuk menilai status hara. Prosesnya ada di data_proxy.py: nilai input dibangkitkan "
        "merata di dalam rentang yang layak, lalu dosis resmi diambil dari tabel sesuai komoditas, target hasil, "
        "dan musim. Pendekatan ini menjamin label selalu sesuai rekomendasi resmi, tidak ada label karangan."))
    c.extend(tabel(
        "Dua belas fitur masukan model",
        ["Kelompok", "Fitur", "Keterangan"],
        [["Kimia tanah", "pH, N persen, P ppm, K me/100g", "dari uji tanah atau dari unit peta"],
         ["Target", "Target hasil (t/ha)", "dipilih petani pada formulir"],
         ["Tekstur (one-hot)", "Lempung, Lempung Liat, Liat", "tiga kolom nol-satu"],
         ["Komoditas (one-hot)", "Padi, Jagung", "dua kolom nol-satu"],
         ["Musim (one-hot)", "Hujan, Kemarau", "dua kolom nol-satu"]],
        [80, 155, 215]))
    c.append(p(
        "Data dibagi dengan seed 42 menjadi 80 persen latih dan 20 persen holdout (1.200 baris). Holdout tidak pernah "
        "disentuh saat pemilihan model, sehingga angka evaluasinya jujur."))

    bagian(5, "Model: Random Forest Regressor")
    c.append(p(
        "Algoritma terpilih adalah Random Forest Regressor dengan 300 pohon dan min_samples_leaf 3. Alasannya tiga. "
        "Pertama, hubungan input-dosis tidak linier karena dosis berubah bertingkat antar kelas tanah dan target "
        "hasil, dan Random Forest menangkap pola seperti itu tanpa perlu rekayasa fitur rumit. Kedua, hutan pohon "
        "tahan terhadap noise dan overfitting bila daun pohon dibatasi. Ketiga, kita butuh perkiraan ketidakpastian, "
        "dan hutan pohon menyediakannya gratis dari sebaran jawaban antarpohon."))
    sub("Cara menghitung keyakinan")
    c.append(p(
        "Setiap pohon menjawab sendiri. Sebaran jawaban antarpohon diukur dengan koefisien variasi rata-rata, lalu "
        "keyakinan dihitung sebagai 1 dikurangi dua kali koefisien variasi, dipotong ke rentang 0 sampai 1. Kalau "
        "pohon-pohon sepakat, keyakinan tinggi. Kalau jawabannya berpencar, keyakinan turun dan aplikasi masuk kategori "
        "ragu. Ini perkiraan, bukan probabilitas statistik yang ketat, dan kami sebut jujur di laporan."))
    sub("Hasil evaluasi resmi (metrik_model.json)")
    c.extend(tabel(None, ["Ukuran", "Uji silang 5-fold", "Holdout 20 persen (1.200 baris)"],
                   [["Agreement dalam rentang pakar", "94,7 persen", "95,2 persen"],
                    ["MAE N", "3,7 kg/ha", "3,6 kg/ha"],
                    ["MAE P", "2,5 kg/ha", "2,4 kg/ha"],
                    ["MAE K", "2,1 kg/ha", "2,1 kg/ha"],
                    ["R2 N", "0,989", "0,990"],
                    ["R2 P", "0,991", "0,991"],
                    ["R2 K", "0,942", "0,943"]],
                   [150, 125, 175]))
    c.append(p(
        "Fitur paling berpengaruh menurut importance model: Komoditas Padi 58,8 persen, Komoditas Jagung 17,2 persen, "
        "N persen 15,0 persen, Target Hasil 3,2 persen, P ppm 2,4 persen. Wajar, karena tabel Permentan memang "
        "pertama-tama memisahkan komoditas dan target hasil."))
    sub("Pelatihan ulang")
    c.append(p(
        "Melatih ulang hanya butuh sekitar 4 detik di laptop tanpa GPU, jadi saat data lapangan pilot terkumpul, "
        "model bisa diperbarui tiap musim tanpa biaya komputasi berarti."))

    bagian(6, "Guardrail, ambang keyakinan, dan keamanan jawaban")
    c.extend(tabel(
        "Enam guardrail yang terpasang dan diuji",
        ["No", "Guardrail", "Cara kerja"],
        [["1", "Kunci rentang Permentan", "dosis keluaran dipotong ke rentang resmi, dikuasikan pada 45 kombinasi ekstrem"],
         ["2", "Penolakan input buruk", "pH di luar 3 sampai 9, N, P, K atau target di luar rentang layak ditolak 422"],
         ["3", "Penanda luar sebaran", "input di luar sebaran data latih menandai hasil dan menyembunyikan angka"],
         ["4", "Ambang keyakinan", "di bawah 0,70 atau luar sebaran berarti kategori tidak yakin"],
         ["5", "Peringatan Balittanah", "pengapuran saat tanah masam, urea dibagi dua tahap saat musim hujan"],
         ["6", "Disclaimer permanen", "teks tetap tampil pada setiap hasil rekomendasi"]],
        [28, 110, 312]))
    c.extend(tabel(
        "Tiga kategori tampilan hasil",
        ["Kategori", "Syarat", "Tampilan", "Aksi untuk petani"],
        [["Yakin (hijau)", "keyakinan 85 persen ke atas", "kartu dosis penuh dengan rentang aman",
          "disclaimer tetap ada, tombol verifikasi penyuluh"],
         ["Ragu (kuning)", "keyakinan 70 sampai 85 persen", "angka dengan rentang aman dan catatan kategori",
          "anjuran cek ulang, verifikasi diperkuat"],
         ["Tidak yakin (merah)", "di bawah 70 persen atau luar sebaran", "angka disembunyikan, tidak ada dosis",
          "diarahkan ke uji tanah lab atau penyuluh"]],
        [85, 100, 120, 145]))
    c.append(p(
        "Teks disclaimer persis seperti ini dan jangan diubah saat presentasi: Rekomendasi awal dari model, bukan "
        "pengganti uji tanah laboratorium. Verifikasi penyuluh sebelum pembelian pupuk."))

    bagian(7, "Peta lahan 191 unit dan pemilihannya")
    c.append(p(
        "Layar peta menggambar 191 unit lanskap hara SAFRONS wilayah Bogor sebagai kanvas SVG mandiri. Tidak ada tile "
        "peta daring, tidak ada pustaka peta eksternal, jadi layar ini tetap terpakai tanpa internet, sesuai kondisi "
        "kuota petani. Warna unit mengikuti kelas pH (masam, agak masam, setengah masam, netral ke subur) dengan "
        "legenda di bawah peta."))
    c.append(p(
        "Cara pemilihannya presisi: ketukan pengguna diuji dengan perhitungan point-in-polygon terhadap seluruh poligon "
        "unit, sehingga unit yang tersorot persis bentuk lahannya, bukan unit terdekat yang terlihat. Setelah unit "
        "dipilih, peta memperbesar ke unit itu, label nama tampil, dan kartu ringkasan pH serta status hara muncul. "
        "Petani tinggal mengisi luas petaknya di dalam unit tersebut."))
    c.append(p(
        "Batas jujur yang perlu diketahui anggota: unit SAFRONS adalah skala lanskap, bukan petak individu. Dua petak "
        "di unit yang sama mendapat perkiraan hara yang sama sampai petani memasukkan hasil uji tanah sendiri. "
        "Keterbatasan ini tertulis di laporan Bab 12."))

    bagian(8, "Fitur aplikasi layar demi layar")
    c.extend(tabel(None, ["Layar", "Fungsi utama"],
                   [["Splash dan persetujuan", "logo, tagline, checkbox persetujuan data sebelum masuk"],
                    ["Beranda", "kartu musim tanam, status lahan, pintasan minta rekomendasi, pesan selamat datang"],
                    ["Lahan saya", "daftar lahan terdaftar, pintasan tambah lahan"],
                    ["Tambah lahan dari peta", "peta 191 unit, pencarian nama, zoom ke unit, info strip unit, isi luas petak"],
                    ["Tambah lahan dari uji tanah", "form pH, N, P, K, tekstur dengan validasi dan penolakan nilai tidak layak"],
                    ["Formulir rekomendasi", "pilih petak, komoditas Padi atau Jagung, target hasil, luas, musim tanam"],
                    ["Hasil rekomendasi", "badge keyakinan, tiga kartu dosis dengan rentang, kebutuhan dan biaya, tiga paket, penjelasan, peringatan"],
                    ["Riwayat", "hasil tersimpan per petak dan per musim"],
                    ["Papan penyuluhan", "tips pemupukan, panel verifikasi penyuluh setujui atau minta koreksi, kontak"],
                    ["Profil", "nama, persetujuan data, hapus semua data, metrik model nyata (agreement, MAE)"],
                    ["Status offline", "chip Online dan pesan lokal saat tanpa koneksi, peta tetap terpakai"]],
                   [120, 330]))

    bagian(9, "Arsitektur teknis dan keputusan penting")
    c.append(p(
        "Backend adalah server Python bawaan (http.server) dengan gaya WSGI sederhana di server.py, membungkus mesin "
        "inferensi model.py. Frontend adalah satu halaman aplikasi (SPA) HTML, CSS, dan JavaScript murni tanpa "
        "framework, dengan state di localStorage perangkat. Model disimpan sebagai model.joblib dan dimuat sekali. "
        "Produksi berjalan di Vercel Python runtime dengan salinan vercel_api yang bebas pandas."))
    c.extend(tabel(
        "Kontrak API",
        ["Metode", "Jalur", "Fungsi"],
        [["POST", "/rekomendasi", "validasi payload, prediksi dosis, keyakinan, guardrail, paket, penjelasan"],
         ["GET", "/model/info", "metrik model resmi untuk layar Profil"],
         ["GET", "/api/peta", "191 unit SAFRONS dalam GeoJSON hasil konversi WGS84"],
         ["GET", "/api/health", "cek kesehatan dan kesiapan model"],
         ["GET", "/ (statis)", "index.html, styles.css, app.js"]],
        [50, 110, 290]))
    sub("Tiga keputusan teknis dan alasannya (sering ditanya juri)")
    c.append(p(
        "Pertama, kenapa server stdlib bukan FastAPI. Pada mesin pengembangan, kebijakan Windows Application Control "
        "memblokir pustaka pydantic-core yang dibutuhkan FastAPI, dan juga scikit-learn versi terbaru. Kami lalu "
        "menulis pembungkus http.server yang kontrak JSON-nya sama persis, dan memakai scikit-learn 1.8.0 yang lolos "
        "kebijakan. Semua kontrak dan pengujian tetap setara dengan desain asli."))
    c.append(p(
        "Kedua, kenapa salinan Vercel bebas pandas. Paket runtime Vercel memasang numpy, scikit-learn, dan joblib "
        "saja, jadi model.py versi produksi mendeklarasikan kolom fitur secara lokal dan memakai array numpy murni "
        "tanpa pandas. Hasil prediksinya identik dengan mesin pengembangan."))
    c.append(p(
        "Ketiga, kenapa peta SVG bukan Leaflet atau tile daring. Percobaan dengan peta daring menghasilkan latar yang "
        "kacau dan pemilihan yang tidak presisi saat sinyal lemah. Kanvas vektor mandiri menyelesaikan keduanya: "
        "ringan, offline, dan ketukan dipetakan lewat point-in-polygon sehingga unit yang tersorot persis bentuknya."))

    bagian(10, "Pengujian: apa yang sudah dibuktikan")
    c.extend(tabel(
        "Kelompok pengujian dan hasil",
        ["Pengujian", "Alat", "Cakupan", "Hasil"],
        [["API dan guardrail", "pytest", "12 pengujian: kontrak, rentang aman, input buruk, luar sebaran, paket",
          "semua lulus"],
         ["Perjalanan antarmuka", "Playwright Chromium 390 px", "20 langkah dari splash sampai profil dan verifikasi",
          "semua lulus, tanpa galat konsol"],
         ["Stres guardrail", "skrip uji", "45 kombinasi input ekstrem", "0 pelanggaran rentang resmi"],
         ["Latensi API", "30 permintaan beruntun", "waktu jawab penuh", "rata-rata 71 ms, p95 87 ms"],
         ["Keandalan model", "uji silang dan holdout", "1.200 baris holdout terpisah", "agreement 95,2 persen"]],
        [95, 95, 145, 115]))
    sub("Temuan terbesar dan penyelesaiannya")
    c.append(p(
        "Keyakinan pita tengah belum terkalibrasi bagus, kelompok Cukup yakin hanya mencapai agreement 42,9 persen, "
        "walaupun kasusnya jarang (1,2 persen). Karena tidak bisa diperbaiki cepat, kategori sedang selalu disertai "
        "rentang aman dan anjuran verifikasi, dan kejujuran ini dilaporkan di Bab 8."))
    c.append(p(
        "Badge keyakinan pernah terpotong pada layar 390 piksel saat uji perjalanan. Sudah diperbaiki dengan memindah "
        "badge ke baris sendiri, dan uji diulang sampai lulus. Ketukan peta sempat memilih unit yang salah, diperbaiki "
        "dengan pengujian point-in-polygon, dibuktikan dengan langkah uji ketukan pada koordinat tertentu yang kini "
        "selalu memilih unit yang tepat."))

    bagian(11, "Ekonomi AI dan model bisnis")
    c.extend(tabel(
        "Perhitungan biaya per prediksi (asumsi server Rp 90.000 per bulan)",
        ["Skenario", "Petani", "Prediksi per bulan", "Biaya per bulan", "Biaya per prediksi"],
        [["Konservatif, 1 poktan", "25", "125", "Rp 90.000", "Rp 720"],
         ["Realistis, 4 poktan", "100", "500", "Rp 90.000", "Rp 180"],
         ["Optimistis, 20 poktan", "500", "2.500", "Rp 180.000", "Rp 72"]],
        [120, 50, 90, 90, 100]))
    c.append(p(
        "Pembanding yang kuat untuk juri: satu uji tanah laboratorium (asumsi Rp 150.000) setara 208 prediksi pada "
        "skenario konservatif. Strategi hemat: model 300 pohon tanpa GPU, penjelasan templat tanpa LLM sehingga biaya "
        "token nol, dan data peta statis. Model bisnis: pilot gratis, kelak iuran poktan sekitar Rp 25.000 per bulan, "
        "titik impas 4 poktan. Bukti kesediaan bayar belum ada dan kami tandai jujur sebagai asumsi pilot. Biaya "
        "selain server: pelatihan ulang Rp 0 (4 detik di laptop), domain sekitar Rp 200.000 per tahun."))

    bagian(12, "Tata kelola, privasi, dan etika")
    c.append(p(
        "Data lahan disimpan di perangkat petani (localStorage), tidak ada server penyimpanan koordinat. Persetujuan "
        "diambil di onboarding dengan teks yang bisa dibaca di splash. Halaman Profil menyediakan saklar tolak "
        "pelatihan model dan tombol hapus semua data yang membersihkan lahan, riwayat, dan verifikasi di perangkat. "
        "Dari sisi bias, data latih bersumber dari tabel resmi sehingga tidak memihak wilayah tertentu, tetapi "
        "cakupannya mengikuti rentang tabel, dan kondisi di luar sebaran tidak pernah diberi angka. Keputusan akhir "
        "selalu manusia: petani dan penyuluh."))

    bagian(13, "Keterbatasan yang jujur (hafalkan untuk tanya jawab)")
    for b in [
        "Data latih masih proxy tabel resmi, bukan hasil uji laboratorium, sehingga validasi lapangan masih "
        "dijadwalkan pada pilot.",
        "Unit peta SAFRONS ber skala lanskap, bukan petak individu, sehingga dua petak dalam satu unit mendapat "
        "perkiraan yang sama sebelum ada uji tanah.",
        "Keyakinan pita tengah belum terkalibrasi bagus (agreement 42,9 persen pada 1,2 persen kasus), "
        "ditangani dengan rentang aman dan anjuran verifikasi, belum dengan kalibrasi ulang.",
        "Penguji usability masih anggota tim, petani sasaran menyusul pada pilot.",
        "Kepuasan petani dan bukti kesediaan bayar belum diukur, dilaporkan apa adanya.",
        "Akun multi pengguna dan sinkronisasi antarperangkat belum ada karena data sengaja di perangkat.",
    ]:
        c.append(p("•  " + b, G_ISI))

    bagian(14, "Rencana lanjutan dan roadmap")
    c.extend(tabel(None, ["Tahap", "Cakupan", "Fokus"],
                   [["Pilot", "1 poktan di Bogor, sekitar 25 petani, musim hujan berikutnya",
                     "validasi persona, kepuasan, kumpulkan data lapangan"],
                    ["Perluasan", "4 sampai 5 poktan, sekitar 100 petani", "pelatihan ulang model dengan data lapangan"],
                    ["Skala", "kerja sama koperasi atau dinas", "perluasan wilayah dan komoditas"]],
                   [70, 180, 200]))
    c.append(p(
        "Fitur yang sengaja ditunda beserta alasannya: draf RDKK otomatis (butuh akumulasi data anggota poktan), "
        "kalender pemupukan pribadi (butuh riwayat petak lintas musim), diagnosis hama dari foto (butuh dataset citra "
        "dan model visi terpisah), dan rilis APK Android (menunggu alur terkonfirmasi petani). Umpan balik "
        "berkelanjutan lewat panel verifikasi penyuluh dan kunjungan poktan tiap dua pekan."))

    bagian(15, "Pembagian penguasaan materi")
    c.extend(tabel(None, ["Anggota", "Membawakan", "Wilayah jawab tanya jawab"],
                   [["Irgi Setiawan", "Slide 1 sampai 4: pembukaan, masalah, solusi AI, demo",
                     "persona, arsitektur teknis, keputusan peta SVG dan server stdlib"],
                    ["Syarif Abdullah Assagaf", "Slide 5 sampai 7: ketidakpastian, pengujian, ekonomi",
                     "metrik, guardrail teruji, kalibrasi keyakinan, perhitungan biaya"],
                    ["Thogianna (Anggi) Sinaga", "Slide 8 sampai 10: tata kelola, adopsi, penutup",
                     "privasi dan consent, risiko, pilot, roadmap, keterbatasan"]],
                   [105, 170, 175]))
    c.append(p(
        "Semua anggota wajib paham dokumen ini secara utuh karena pertanyaan juri bisa diarahkan ke siapa saja. "
        "Kalau jawaban ada di luar bagian masing-masing, boleh meneruskan ke teman dengan kalimat: terkait bagian "
        "itu, teman kami yang lebih paham detailnya, silakan Syarif atau Anggi atau Irgi menambahkan."))

    bagian(16, "Kamus istilah")
    c.extend(tabel(None, ["Istilah", "Arti dalam proyek ini"],
                   [["N, P, K", "unsur makro tanaman: nitrogen, fosfor, kalium, tiga angka dosis yang diprediksi"],
                    ["kg/ha", "kilogram pupuk per hektar lahan, satuan dosis unsur"],
                    ["Urea, SP-36, KCl", "tiga pupuk niaga pembawa N, P, dan K yang dihitung per petak"],
                    ["pH tanah", "tingkat keasaman tanah, memengaruhi ketersediaan hara"],
                    ["ppm dan me/100g", "satuan hasil uji tanah untuk P dan K"],
                    ["Permentan 40/2007", "peraturan tabel rekomendasi dosis resmi padi dan jagung"],
                    ["Balittanah", "lembaga penelitian tanah, sumber kaidah interpretasi kesuburan dan peringatan"],
                    ["SAFRONS", "sistem informasi lahan pertanian pangan yang menyediakan peta hara 191 unit Bogor"],
                    ["Lanskap", "unit peta berskala wilayah, bukan petak individu milik satu petani"],
                    ["poktan", "kelompok petani, mitra utama pilot dan calon pembayar langganan"],
                    ["Random Forest", "kumpulan pohon keputusan yang rata-rata jawabannya jadi prediksi"],
                    ["agreement", "persentase prediksi yang jatuh di kelas dosis yang sama dengan rekomendasi pakar"],
                    ["MAE", "rata-rata selisih mutlak prediksi terhadap label, dalam kg/ha"],
                    ["holdout", "20 persen data yang disisihkan dan hanya dipakai saat evaluasi akhir"],
                    ["guardrail", "pengaman aturan yang mengunci atau menyembunyikan keluaran model"],
                    ["keyakinan", "angka 0 sampai 1 dari sebaran jawaban antarpohon hutan"],
                    ["luar sebaran", "input di luar wilayah data latih, angka tidak boleh tampil"],
                    ["RDKK", "rencana defisit dan kebutuhan kelompok, dokumen pengajuan pupuk bersubsidi"],
                    ["localStorage", "penyimpanan kecil di peramban, tempat semua data lahan petani disimpan"],
                    ["p95", "persentil 95, angka yang dilampaui hanya 5 persen permintaan terlambat"]],
                   [95, 355]))

    bagian(17, "Tanya jawab cepat, sepuluh pertanyaan paling mungkin")
    faq = [
        ("Kenapa Random Forest, bukan regresi linier?",
         "Hubungan input ke dosis bertingkat dan tidak linier karena mengikuti tabel resmi per komoditas, target "
         "hasil, dan musim. Random Forest menangkap tangga-tangga itu tanpa rekayasa fitur, tahan noise, dan "
         "bukti empirisnya agreement 95,2 persen dengan MAE di bawah 4 kg/ha pada data uji terpisah."),
        ("Kenapa tidak deep learning atau LLM?",
         "Data latih tabular hanya 6.000 baris berlabel resmi, Random Forest sudah melampaui target dengan komputasi "
         "empat detik tanpa GPU. Untuk angka, LLM berisiko mengarang dan berbiaya token, sedangkan penjelasan dari "
         "templat sudah memadai dan aman."),
        ("Data latihnya dari mana, apakah hasil lab?",
         "Bukan. Data proxy 6.000 baris diekstraksi dari tabel Permentan 40/2007 dengan kaidah Balittanah, jadi label "
         "selalu sesuai rekomendasi resmi. Keterbatasannya jujur kami tulis: validasi lapangan lewat pilot belum "
         "selesai."),
        ("Bagaimana kalau input petani aneh atau ekstrem?",
         "Tiga lapis: input di luar rentang layak ditolak dengan pesan jelas, input di dalam rentang tetapi di luar "
         "sebaran data latih menandai hasil dan menyembunyikan angka, dan semua keluaran tetap dipotong ke rentang "
         "resmi. Empat puluh lima kombinasi ekstrem sudah diuji, nol pelanggaran."),
        ("Apakah aplikasi ini menggantikan penyuluh?",
         "Tidak. PupukPintar menghitung usulan awal, penyuluh memverifikasi. Tombol Kirim ke Penyuluh ada di setiap "
         "hasil dan panel verifikasinya ada di Papan Penyuluhan, jadi keputusan akhir tetap manusia."),
        ("Keyakinan dihitung bagaimana, kenapa bisa dipercaya?",
         "Dari sebaran jawaban 300 pohon: pohon yang sepakat berarti keyakinan tinggi, pohon yang berpencar berarti "
         "rendah. Ini perkiraan yang jujur kami sebut demikian, dan ambangnya 85 persen yakin, 70 sampai 85 ragu, "
         "di bawah itu angka disembunyikan."),
        ("Bagaimana memastikan angka evaluasi tidak bocor?",
         "Holdout 20 persen dengan seed berbeda disisihkan sejak awal dan tidak pernah disentuh saat pemilihan model. "
         "Angka 95,2 persen hanya dihitung sekali di akhir pada 1.200 baris tersebut."),
        ("Kalau petani tidak punya hasil uji tanah?",
         "Pilih unit lahannya di peta 191 unit SAFRONS, pH dan status hara unit otomatis terpakai sebagai input. "
         "Kalau kelak ada hasil lab, jalur uji tanah memberi hasil yang lebih presisi."),
        ("Kenapa peta tidak memakai Google Maps?",
         "Peta daring membutuhkan kuota dan koneksi yang tidak selalu ada di lahan, dan percobaan kami menghasilkan "
         "latar kacau serta pemilihan tidak presisi. Kanvas vektor mandiri ringan, jalan offline, dan ketukan dipilih "
         "persis lewat point-in-polygon pada 191 poligon unit."),
        ("Bagaimana produk ini menghasilkan uang?",
         "Pilot gratis. Kelak iuran poktan sekitar Rp 25.000 per bulan untuk rekap kebutuhan anggota, dengan biaya "
         "server Rp 90.000 per bulan, titik impas empat poktan. Bukti kesediaan bayar belum ada dan kami jujur "
         "menandainya sebagai asumsi untuk divalidasi saat pilot."),
    ]
    for i, (q, a) in enumerate(faq, 1):
        c.append(p("%d.  %s" % (i, q), G_H2))
        c.append(p(a, G_ISI))

    dok.build(c)
    print("selesai:", dok.filename)


if __name__ == "__main__":
    bangun_skrip()
    bangun_pengetahuan()
