# -*- coding: utf-8 -*-
"""Patch satu kali: perbarui pembangkit laporan untuk peta SAFRONS asli."""

p = "laporan/pembangkit/buat_laporan.py"
s = open(p, encoding="utf-8").read()
ganti = [
    ('["Input lahan lewat peta zona contoh atau hasil uji tanah"',
     '["Input lahan lewat peta hara SAFRONS atau hasil uji tanah"'),
    ('["Spasial", "Zona peta hara wilayah Bogor untuk input cepat", "Tidak dipakai melatih", "Data contoh representasi 12 zona (gen_zona.py), terinspirasi peta 191 area SAFRONS", "12 zona contoh", "Penandaan zona ke nilai hara contoh, diberi label jelas sebagai contoh di antarmuka"]',
     '["Spasial", "Peta hara 191 area wilayah Bogor untuk input cepat (pH rata-rata dan band N-P-K)", "Tidak dipakai melatih", "Data spasial asli SAFRONS dari kode yang kami audit (hara-bogor.geojson, diproses gen_peta.py)", "191 area, 3 di antaranya tanpa data", "Konversi proyeksi UTM ke WGS84, penyederhanaan geometri, pemetaan band N-P-K ke nilai perwakilan skala model (Lampiran C)"]'),
    ('"Input uji tanah atau zona peta"', '"Input uji tanah atau peta hara SAFRONS"'),
    ('["Jumlah data yang ditulis adalah jumlah nyata", "Terpenuhi (6.000 baris proxy, 12 zona contoh)"]',
     '["Jumlah data yang ditulis adalah jumlah nyata", "Terpenuhi (6.000 baris proxy, 191 area peta SAFRONS)"]'),
    ('["In-scope", "Registrasi lahan (peta zona contoh atau uji tanah)',
     '["In-scope", "Registrasi lahan (peta hara SAFRONS atau uji tanah)'),
    ('["Sumber input peta", "Peta 191 area SAFRONS", "Peta zona contoh representasi 12 zona wilayah Bogor", "Data SAFRONS tidak terbuka mudah untuk demo, zona contoh diberi label jujur sebagai contoh di antarmuka"]',
     '["Sumber input peta", "Peta 191 area SAFRONS", "Data spasial asli SAFRONS (191 area) dari kode yang kami audit, dengan konversi band ke skala model", "Data asli ternyata tersedia di repositori audit sehingga demo memakai peta sungguhan, bukan representasi"]'),
    ('["F-02", "Daftar lahan via peta zona atau uji tanah", "Sebagai petani, saya ingin mendaftarkan lahan dengan memilih zona di peta atau memasukkan hasil uji tanah, agar kondisi hara lahan saya dikenali tanpa lab"',
     '["F-02", "Daftar lahan via peta hara SAFRONS atau uji tanah", "Sebagai petani, saya ingin mendaftarkan lahan dengan menandai areanya di peta atau memasukkan hasil uji tanah, agar kondisi hara lahan saya dikenali tanpa lab"'),
    ('["F-02", "Lahan Saya, tambah lahan, peta zona, uji tanah", "GET /api/zona, SVG interaktif 12 zona, formulir uji tanah dengan validasi", "S-02, S-03"]',
     '["F-02", "Lahan Saya, tambah lahan, peta hara, uji tanah", "GET /api/peta, peta Leaflet interaktif 191 area SAFRONS, formulir uji tanah dengan validasi", "S-02, S-03"]'),
    ('gambar(os.path.join(LAYAR, "04-peta-zona.png"), "Gambar 6.8 Peta zona contoh untuk pendaftaran lahan", 6.4)',
     'gambar(os.path.join(LAYAR, "04-peta-hara.png"), "Gambar 6.8 Peta hara 191 area SAFRONS di atas basemap OpenStreetMap (Leaflet) untuk pendaftaran lahan", 6.4)'),
    ('["Keyakinan tinggi (0,85 ke atas)", "Badge hijau Keyakinan 90 persen (Yakin), tiga kartu dosis, biaya, paket", "Keyakinan 90% (Yakin)"',
     '["Keyakinan tinggi (0,85 ke atas)", "Badge hijau Keyakinan 91 persen (Yakin), tiga kartu dosis, biaya, paket", "Keyakinan 91% (Yakin)"'),
    ('["/api/zona", "GET", "Tanpa body", "JSON 12 zona contoh dengan pH, N, P, K, tekstur, koordinat gambar"]',
     '["/api/peta", "GET", "Tanpa body", "JSON 191 area SAFRONS: nama, pH rata-rata, band dan nilai perwakilan N-P-K, tekstur, geometri ringkas"]'),
    ('["F-02", "Gambar 6.8 (peta zona) dan langkah lahan dari peta serta uji tanah", "Ya", "Dua jalur input teruji, validasi pH 9,4 menolak"]',
     '["F-02", "Gambar 6.8 (peta hara SAFRONS) dan langkah lahan dari peta serta uji tanah", "Ya", "Dua jalur input teruji, validasi pH 9,4 menolak"]'),
    ('["Peta 191 area SAFRONS tidak tersedia sebagai data terbuka yang mudah dipakai demo", "Menyalin data penuh, menunggu izin, atau membuat representasi contoh", "Peta zona contoh 12 zona dengan label jujur sebagai contoh di antarmuka dan laporan", "Alur pendaftaran via peta tetap teruji tanpa mengklaim data yang bukan milik kami"]',
     '["Koordinat peta SAFRONS ternyata tersimpan dalam proyeksi UTM meter meski berkas .prj mengaku WGS84, dan satuan N-P-K tidak dideklarasikan pada sumbernya", "Memakai apa adanya (peta melenceng), menunggu kepastian satuan, atau mengonversi sendiri dengan dokumentasi lengkap", "Konversi UTM 48S ke WGS84 memakai rumus Transverse Mercator inverse (gen_peta.py), dan N-P-K dipetakan dari band kuintil SAFRONS ke nilai perwakilan skala model (Lampiran C)", "Peta sungguhan 191 area terpakai di demo, konversi dapat diperiksa siapa pun, status hara hasil peta konsisten dengan interpretasi Balittanah kami"]'),
    ('["S-02", "Mendaftar lahan dari peta zona (pilih zona, isi nama, pakai zona)", "F-02", "Lahan muncul di daftar dengan chip status hara"]',
     '["S-02", "Mendaftar lahan dari peta hara (ketuk area, isi nama, pakai area)", "F-02", "Lahan muncul di daftar dengan chip status hara"]'),
    ('["Data peta statis", "Zona disajikan dari berkas JSON statis lewat GET /api/zona", "Tidak ada query basis data per kunjungan peta"]',
     '["Data peta statis", "Peta 191 area disajikan dari berkas GeoJSON statis ringkas lewat GET /api/peta", "Tidak ada query basis data per kunjungan peta"]'),
    ('["Beban mengisi data uji tanah", "Petani tidak punya angka lab", "Jalur peta zona tanpa angka, atau input kasar yang tetap dijaga guardrail"]',
     '["Beban mengisi data uji tanah", "Petani tidak punya angka lab", "Jalur peta hara tanpa angka, atau input kasar yang tetap dijaga guardrail"]'),
    ('Komoditas terbatas padi dan jagung, wilayah menyasar Bogor. Data peta zona adalah contoh representasi. Panel penyuluh',
     'Komoditas terbatas padi dan jagung, wilayah menyasar Bogor. Nilai N-P-K dari peta memakai konversi band yang disederhanakan, bukan hasil uji lab per petak. Panel penyuluh'),
    ('sumber input peta menjadi zona contoh berlabel jujur',
     'sumber input peta berpindah dari rencana zona contoh ke peta spasial asli SAFRONS'),
    ('model info dan zona', 'model info dan peta'),
    ('["Label zona peta panjang menimpa zona tetangga", "Tangkapan layar peta sebelum perbaikan", "Label Megamendung terpotong", "Rendah", "Lebar kotak zona menyesuaikan panjang nama, disusun per baris, uji ulang lulus"]',
     '["Peta grid awal berupa representasi buatan, bukan data asli", "Perbandingan peta versi awal dengan data sumber SAFRONS", "Input lahan tidak memakai peta sungguhan", "Rendah", "Diganti peta spasial asli 191 area SAFRONS (Leaflet) setelah data ditemukan di repositori audit"]'),
    ('["2", "Tata letak zona peta disusun ulang per baris dengan lebar dinamis", "Label panjang menimpa zona tetangga"]',
     '["2", "Peta grid 12 zona diganti peta spasial asli 191 area SAFRONS (Leaflet, basemap OpenStreetMap)", "Data asli ditemukan di repositori audit sehingga representasi buatan tidak lagi diperlukan"]'),
]
for lama, baru in ganti:
    assert lama in s, "TIDAK KETEMU: " + lama[:70]
    s = s.replace(lama, baru)

tabel_map = (
    '    p("Pemetaan band SAFRONS ke nilai perwakilan skala model (peta wilayah):")\n'
    '    tabel("Tabel C.1 Konversi band N-P-K peta SAFRONS ke nilai uji tanah model", '
    '["Band SAFRONS", "Ambang pemisah band (nilai sumber)", "N (persen)", "P (ppm)", "K (me/100g)"], [\n'
    '        ["Sangat rendah", "N di bawah 2,0, P di bawah 6,7, K di bawah 147,0", "0,07", "3,0", "0,06"],\n'
    '        ["Rendah", "N di bawah 2,5, P di bawah 7,8, K di bawah 197,5", "0,15", "8,0", "0,15"],\n'
    '        ["Sedang", "N di bawah 4,2, P di bawah 8,0, K di bawah 331,2", "0,30", "18,0", "0,30"],\n'
    '        ["Tinggi", "N di bawah 5,5, P di bawah 9,0, K di bawah 447,9", "0,50", "40,0", "0,60"],\n'
    '        ["Sangat tinggi", "nilai pada atau di atas ambang terakhir", "0,85", "90,0", "1,00"],\n'
    '    ], lebar=[3.0, 6.6, 2.2, 2.2, 2.0], ukuran=9.5)\n'
    '    p("Nilai perwakilan dipilih agar status hara menurut batas kelas Balittanah yang kami pakai (Bab 3) '
    'jatuh pada kelas yang sama dengan band aslinya, sehingga rekomendasi dari peta konsisten dengan pembacaan SAFRONS. '
    'Area tanpa data (3 area) tidak dapat dipilih, meniru perilaku SAFRONS.")\n\n'
    '    h2("Lampiran D. Hasil pengujian (data mentah)")'
)
kunci = '    h2("Lampiran D. Hasil pengujian (data mentah)")'
assert kunci in s
s = s.replace(kunci, tabel_map)

open(p, "w", encoding="utf-8").write(s)
print("laporan diperbarui, semua 21 penggantian sukses")
