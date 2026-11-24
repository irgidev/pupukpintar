# -*- coding: utf-8 -*-
"""
Pembangkit data peta hara PupukPintar dari data spasial asli SAFRONS.

Sumber: lkp1/Kode Program CAPS-32/backend/reference/data-hara-bogor/hara-bogor.geojson
(191 area wilayah Bogor dan sekitarnya, hasil audit LKP-P1).

Konversi yang dilakukan (terdokumentasi di Laporan Akhir, Lampiran C):
- pH_rata2 dipakai langsung (pH bebas satuan).
- N, P, K pada data SAFRONS dipakai secara RELATIF oleh SAFRONS sendiri
  (lima band kuintil, ambang di app/services/hara_diagnosis.py), tanpa
  klaim satuan laboratorium. Karena itu band SAFRONS dipetakan ke nilai
  perwakilan pada skala uji tanah model kami, dipilih agar status hara
  menurut kaidah Balittanah yang kami pakai tetap konsisten dengan band
  aslinya.
- TEXTURE_OF (deskripsi multi-lapisan tanah) diambil lapisan atasnya dan
  dikelaskan ke tiga kelas model: Lempung, Lempung Liat, atau Liat.
- Area tanpa data (water, no data, nilai -9999) ditandai nodata dan tidak
  dapat dipilih, meniru perilaku SAFRONS.
- Geometri disederhanakan: koordinat dibulatkan 4 desimal dan titik
  berurutan yang sama dibuang (presisi sekitar 11 meter, cukup untuk
  pemilihan area pada tingkat zoom aplikasi).

Jalankan dari folder app/frontend/data:
    python gen_peta.py <jalur-hara-bogor.geojson>
"""

import json
import math
import os
import sys

# ----------------------------------------------------------------------
# konversi UTM ke WGS84
# Koordinat pada hara-bogor.geojson ternyata proyeksi UTM (meter, zona 48
# belahan selatan) meski berkas .prj mengaku WGS84. Konversi memakai rumus
# inverse Transverse Mercator standar (seri USGS Professional Paper 1395).
# ----------------------------------------------------------------------

K0 = 0.9996
A = 6378137.0
F = 1 / 298.257223563
E2 = F * (2 - F)
E4 = E2 * E2
E6 = E4 * E2
EP2 = E2 / (1 - E2)


def utm_ke_latlon(easting, northing, zona):
    x = easting - 500000.0
    m = (northing - 10000000.0) / K0  # belahan selatan
    mu = m / (A * (1 - E2 / 4 - 3 * E4 / 64 - 5 * E6 / 256))
    e1 = (1 - math.sqrt(1 - E2)) / (1 + math.sqrt(1 - E2))
    j1 = 3 * e1 / 2 - 27 * e1 ** 3 / 32
    j2 = 21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32
    j3 = 151 * e1 ** 3 / 96
    j4 = 1097 * e1 ** 4 / 512
    fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)

    c1 = EP2 * math.cos(fp) ** 2
    t1 = math.tan(fp) ** 2
    n1 = A / math.sqrt(1 - E2 * math.sin(fp) ** 2)
    r1 = A * (1 - E2) / (1 - E2 * math.sin(fp) ** 2) ** 1.5
    d = x / (n1 * K0)

    lat = fp - (n1 * math.tan(fp) / r1) * (
        d ** 2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * EP2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * EP2 - 3 * c1 ** 2) * d ** 6 / 720
    )
    lon = math.radians((zona - 1) * 6 - 180 + 3) + (
        d
        - (1 + 2 * t1 + c1) * d ** 3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * EP2 + 24 * t1 ** 2) * d ** 5 / 120
    ) / math.cos(fp)
    return math.degrees(lon), math.degrees(lat)


ZONA = 48  # Jawa bagian barat


def konversi_ring(ring):
    hasil = []
    for titik in ring:
        x, y = titik[0], titik[1]
        if x > 180:  # masih meter UTM, konversi
            lon, lat = utm_ke_latlon(x, y, ZONA)
        else:  # sudah derajat
            lon, lat = x, y
        t = (round(lon, 4), round(lat, 4))
        if not hasil or t != hasil[-1]:
            hasil.append(t)
    return hasil

# ambang band SAFRONS, disalin persis dari app/services/hara_diagnosis.py
AMBANG_SAFRONS = {
    "n": (1.989691, 2.450581, 4.158587, 5.5412572),
    "p": (6.672457, 7.790811, 8.022388, 8.970512),
    "k": (146.97696, 197.49262, 331.24494, 447.9228),
}
LABEL_BAND = ["sangat rendah", "rendah", "sedang", "tinggi", "sangat tinggi"]

# nilai perwakilan pada skala model (N persen, P ppm, K me/100g), dipilih
# agar jatuh di kelas Balittanah yang sama dengan band aslinya
NILAI_PERWAKILAN = {
    "n": [0.07, 0.15, 0.30, 0.50, 0.85],
    "p": [3.0, 8.0, 18.0, 40.0, 90.0],
    "k": [0.06, 0.15, 0.30, 0.60, 1.00],
}


def band_dari_nilai(nilai, ambang):
    if nilai is None or nilai == -9999:
        return None
    for i, a in enumerate(ambang):
        if nilai < a:
            return i
    return 4


def kelas_tekstur(teks):
    if not teks:
        return "Lempung"
    lapis_atas = teks.split("/")[0].strip().lower()
    if lapis_atas.startswith("mod. fine") or lapis_atas.startswith("mod.fine"):
        return "Lempung Liat"
    if lapis_atas.startswith("fine"):
        return "Liat"
    return "Lempung"


def ringkas_koordinat(ring):
    hasil = []
    for titik in ring:
        x, y = titik[0], titik[1]
        t = (round(x, 4), round(y, 4))
        if not hasil or t != hasil[-1]:
            hasil.append(t)
    return hasil


def ringkas_geometri(geo):
    if geo["type"] == "Polygon":
        return {"type": "Polygon", "coordinates": [konversi_ring(r) for r in geo["coordinates"]]}
    return {
        "type": "MultiPolygon",
        "coordinates": [[konversi_ring(r) for r in poly] for poly in geo["coordinates"]],
    }


def utama(jalur_sumber, jalur_keluar):
    with open(jalur_sumber, encoding="utf-8") as f:
        g = json.load(f)

    fitur = []
    n_nodata = 0
    for f in g["features"]:
        p = f["properties"]
        nama = (p.get("NAME") or "").strip()
        ph = p.get("pH_rata2")
        nodata = (ph in (-9999, None)) or nama.lower() in ("water", "no data")

        b_n = band_dari_nilai(p.get("N_rata2"), AMBANG_SAFRONS["n"])
        b_p = band_dari_nilai(p.get("P_rata2"), AMBANG_SAFRONS["p"])
        b_k = band_dari_nilai(p.get("K_rata2"), AMBANG_SAFRONS["k"])
        if b_n is None or b_p is None or b_k is None:
            nodata = True

        if nodata:
            n_nodata += 1
            props = {
                "id": p.get("OBJECTID"),
                "nama": nama or "Area tanpa data",
                "nodata": True,
            }
        else:
            props = {
                "id": p.get("OBJECTID"),
                "nama": nama,
                "unit": p.get("UNITNAME"),
                "lereng": p.get("SLOPE__"),
                "pH": round(float(ph), 2),
                "n_band": LABEL_BAND[b_n],
                "p_band": LABEL_BAND[b_p],
                "k_band": LABEL_BAND[b_k],
                "n_persen": NILAI_PERWAKILAN["n"][b_n],
                "p_ppm": NILAI_PERWAKILAN["p"][b_p],
                "k_me100g": NILAI_PERWAKILAN["k"][b_k],
                "tekstur": kelas_tekstur(p.get("TEXTURE_OF")),
                "nodata": False,
            }
        fitur.append({"type": "Feature", "properties": props, "geometry": ringkas_geometri(f["geometry"])})

    hasil = {
        "keterangan": (
            "Peta hara wilayah Bogor dan sekitarnya, data spasial asli SAFRONS (191 area, audit LKP-P1). "
            "pH memakai nilai rata-rata area. N, P, K pada sumber dipakai relatif (band kuintil SAFRONS) "
            "dan dipetakan ke nilai perwakilan pada skala uji tanah model, lihat Laporan Akhir Lampiran C. "
            "Area tanpa data tidak dapat dipilih."
        ),
        "sumber": "SAFRONS, Tim CAPS-32 Ilmu Komputer IPB (hara-bogor.geojson)",
        "features": fitur,
    }
    with open(jalur_keluar, "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, separators=(",", ":"))
    print(f"fitur: {len(fitur)} | tanpa data: {n_nodata} | ukuran: {round(os.path.getsize(jalur_keluar) / 1024, 1)} KB")
    print("tersimpan:", jalur_keluar)


if __name__ == "__main__":
    dasar_repo = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    sumber = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        dasar_repo, "..", "lkp1", "Kode Program CAPS-32", "backend", "reference", "data-hara-bogor", "hara-bogor.geojson")
    keluar = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "peta_safrons.json")
    utama(sumber, keluar)
