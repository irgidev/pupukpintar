# -*- coding: utf-8 -*-
"""
Pengujian API dan guardrail PupukPintar.

Jalankan dari root repositori:
    python -m pytest tests/test_api.py -v

Mengangkat server pada port uji lalu memeriksa: bentuk kontrak API,
guardrail rentang aman, deteksi di luar sebaran data latih, penolakan
input buruk, konsistensi deterministik, konversi dan biaya, paket, dan
latensi p95.
"""

import http.client
import json
import os
import sys
import threading
import time

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app", "backend"))

PORT_UJI = 8765


def _angkat_server():
    import server
    srv = server.ThreadingHTTPServer(("127.0.0.1", PORT_UJI), server.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


SERVER = _angkat_server()

INPUT_DASAR = {
    "pH": 5.8, "n_persen": 0.35, "p_ppm": 8.0, "k_me100g": 0.18,
    "tekstur": "Lempung", "komoditas": "Padi",
    "target_hasil_t_ha": 6.0, "luas_ha": 0.75, "musim": "Hujan",
}

RENTANG = {"Padi": (150, 250, 50, 100, 25, 75), "Jagung": (200, 350, 100, 200, 40, 100)}


def panggil(payload, metode="POST", jalur="/rekomendasi"):
    k = http.client.HTTPConnection("127.0.0.1", PORT_UJI, timeout=30)
    body = json.dumps(payload) if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    k.request(metode, jalur, body=body, headers=headers)
    r = k.getresponse()
    isi = r.read()
    k.close()
    return r.status, json.loads(isi)


def test_kontrak_benar():
    status, h = panggil(INPUT_DASAR)
    assert status == 200
    for kunci in ("dosis_kg_ha", "keyakinan", "kebutuhan_petak_kg",
                  "estimasi_biaya_idr", "paket", "penjelasan", "disclaimer"):
        assert kunci in h, f"field {kunci} tidak ada"
    assert set(h["kebutuhan_petak_kg"]) == {"Urea", "SP36", "KCl"}
    assert set(h["paket"]) == {"hemat", "standar", "optimal"}


def test_guardrail_rentang_aman_padi():
    """Keluaran selalu di dalam rentang Permentan, bahkan untuk input ekstrem."""
    lo = RENTANG["Padi"][0::2]
    hi = RENTANG["Padi"][1::2]
    for pH in (4.0, 5.0, 6.0, 7.0, 8.0):
        for n in (0.05, 0.5, 1.05):
            for p_ppm in (3, 30, 115):
                status, h = panggil({**INPUT_DASAR, "pH": pH, "n_persen": n, "p_ppm": p_ppm,
                                     "target_hasil_t_ha": 8.0})
                assert status == 200
                d = h["dosis_kg_ha"]
                assert lo[0] <= d["N"] <= hi[0], (pH, n, p_ppm, d)
                assert lo[1] <= d["P"] <= hi[1], (pH, n, p_ppm, d)
                assert lo[2] <= d["K"] <= hi[2], (pH, n, p_ppm, d)


def test_guardrail_rentang_aman_jagung():
    lo = RENTANG["Jagung"][0::2]
    hi = RENTANG["Jagung"][1::2]
    status, h = panggil({**INPUT_DASAR, "komoditas": "Jagung", "target_hasil_t_ha": 10.5,
                         "pH": 4.2, "n_persen": 1.0, "k_me100g": 1.1})
    d = h["dosis_kg_ha"]
    assert lo[0] <= d["N"] <= hi[0]
    assert lo[1] <= d["P"] <= hi[1]
    assert lo[2] <= d["K"] <= hi[2]


def test_luar_sebaran_tidak_menampilkan_angka():
    """P 150 ppm di luar sebaran latih -> angka disembunyikan."""
    status, h = panggil({**INPUT_DASAR, "p_ppm": 150.0})
    assert status == 200
    assert h["luar_sebaran_data_latih"] is True
    assert h["tampilkan_angka"] is False
    assert h["dosis_kg_ha"] is None
    assert any("laboratorium" in p.lower() for p in h["peringatan"])


def test_input_buruk_ditolak():
    status, h = panggil({**INPUT_DASAR, "pH": 9.4})
    assert status == 422
    assert "pH" in h["detail"]["pesan"][0]
    status2, h2 = panggil({**INPUT_DASAR, "komoditas": "Cabai"})
    assert status2 == 422
    status3, h3 = panggil({**INPUT_DASAR, "pH": "lima"})
    assert status3 == 422


def test_deterministik():
    """Input sama menghasilkan keluaran sama (uji keandalan Bab 8)."""
    _, h1 = panggil(INPUT_DASAR)
    _, h2 = panggil(INPUT_DASAR)
    assert h1["dosis_kg_ha"] == h2["dosis_kg_ha"]
    assert h1["keyakinan"] == h2["keyakinan"]
    assert h1["estimasi_biaya_idr"] == h2["estimasi_biaya_idr"]


def test_konsistensi_konversi_dan_biaya():
    """Konversi kg/ha -> kg petak dan biaya sesuai kadar unsur dan harga."""
    _, h = panggil(INPUT_DASAR)
    d = h["dosis_kg_ha"]
    keb = h["kebutuhan_petak_kg"]
    luas = INPUT_DASAR["luas_ha"]
    assert keb["Urea"] == round(d["N"] * luas / 0.46)
    assert keb["SP36"] == round(d["P"] * luas / 0.30)
    assert keb["KCl"] == round(d["K"] * luas / 0.60)
    biaya = keb["Urea"] * 2250 + keb["SP36"] * 2300 + keb["KCl"] * 5000
    assert h["estimasi_biaya_idr"] == biaya


def test_paket_dalam_rentang_dan_urut_biaya():
    _, h = panggil({**INPUT_DASAR, "komoditas": "Jagung"})
    lo = RENTANG["Jagung"][0::2]
    hi = RENTANG["Jagung"][1::2]
    b = [h["paket"][p]["estimasi_biaya_idr"] for p in ("hemat", "standar", "optimal")]
    assert b[0] <= b[1] <= b[2]
    for p in ("hemat", "standar", "optimal"):
        d = h["paket"][p]["dosis_kg_ha"]
        assert lo[0] <= d["N"] <= hi[0] and lo[1] <= d["P"] <= hi[1] and lo[2] <= d["K"] <= hi[2]


def test_peringatan_ph_masam():
    _, h = panggil({**INPUT_DASAR, "pH": 4.3})
    assert any("apur" in p for p in h["peringatan"])


def test_model_info_dan_zona():
    status, m = panggil(None, "GET", "/model/info")
    assert status == 200
    assert m["cv"]["agreement_persen"] > 90
    status2, z = panggil(None, "GET", "/api/zona")
    assert status2 == 200
    assert len(z["zona"]) == 12


def test_berkas_statista_dilayani():
    k = http.client.HTTPConnection("127.0.0.1", PORT_UJI, timeout=10)
    k.request("GET", "/")
    r = k.getresponse()
    isi = r.read().decode("utf-8")
    k.close()
    assert r.status == 200
    assert "PupukPintar" in isi


def test_latensi_p95():
    """Target NFR: respons kurang dari 5 detik; kenyataannya jauh di bawah."""
    waktu = []
    for _ in range(20):
        t0 = time.perf_counter()
        status, _ = panggil(INPUT_DASAR)
        assert status == 200
        waktu.append((time.perf_counter() - t0) * 1000)
    waktu.sort()
    p95 = waktu[int(0.95 * (len(waktu) - 1))]
    assert p95 < 5000, f"p95 {p95} ms melebihi 5000 ms"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
