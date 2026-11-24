# -*- coding: utf-8 -*-
"""
Server aplikasi PupukPintar (pustaka standar Python, tanpa dependensi web).

Latar keputusan: pustaka FastAPI/pydantic tersedia di lingkungan pengembangan
kami, tetapi ekstensi biner pydantic-core diblokir oleh kebijakan Application
Control pada sebagian mesin anggota tim. Kontrak API LKP-P6 tidak berubah, jadi
server demo ini dibangun di atas http.server bawaan Python. Untuk penyebaran
produksi, kontrak yang sama tinggal dipindahkan ke FastAPI (lihat laporan Bab 7).

Menyajikan:
    POST /rekomendasi   : kontrak API model AI (LKP-P6, diperluas paket+penjelasan)
    GET  /model/info    : metrik model untuk transparansi pengguna
    GET  /api/zona      : data contoh zona peta hara wilayah Bogor
    GET  /api/health    : status layanan
    GET  /*             : antarmuka web (folder ../frontend)

Jalankan:
    python server.py [port]     (bawaan port 8000)
"""

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import model as mesin

BASE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.normpath(os.path.join(BASE, "..", "frontend"))


class Handler(BaseHTTPRequestHandler):
    server_version = "PupukPintar/1.0"

    # ---------- util keluaran ----------
    def kirim_json(self, obj, status=200):
        isi = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(isi)))
        self.end_headers()
        self.wfile.write(isi)

    def kirim_galat(self, status, jenis, pesan):
        self.kirim_json({"detail": {"jenis": jenis, "pesan": pesan}}, status)

    def kirim_berkas(self, path):
        if not os.path.isfile(path):
            return self.kirim_galat(404, "tidak_ada", "Berkas tidak ditemukan")
        tipe = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if tipe.startswith("text/") or tipe in ("application/javascript", "image/svg+xml"):
            tipe += "; charset=utf-8"
        with open(path, "rb") as f:
            isi = f.read()
        self.send_response(200)
        self.send_header("Content-Type", tipe)
        self.send_header("Content-Length", str(len(isi)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(isi)

    # ---------- util masukan ----------
    def baca_body_json(self):
        panjang = int(self.headers.get("Content-Length") or 0)
        if panjang <= 0:
            return None, "Body kosong"
        try:
            return json.loads(self.rfile.read(panjang).decode("utf-8")), None
        except json.JSONDecodeError:
            return None, "Body bukan JSON yang sah"

    def validasi_payload(self, p):
        """Validasi bentuk payload; kembalikan daftar pesan galat."""
        galat = []
        angka = ("pH", "n_persen", "p_ppm", "k_me100g", "target_hasil_t_ha", "luas_ha")
        for k in angka:
            v = p.get(k)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                galat.append(f"{k} wajib berupa angka")
        if galat:
            return galat
        return mesin.validasi(p)

    # ---------- rute ----------
    def do_POST(self):
        if self.path.rstrip("/") != "/rekomendasi":
            return self.kirim_galat(404, "tidak_ada", "Endpoint tidak dikenal")
        payload, salah = self.baca_body_json()
        if salah:
            return self.kirim_galat(400, "input_buruk", [salah])

        galat = self.validasi_payload(payload)
        if galat:
            return self.kirim_galat(422, "input_buruk", galat)

        import time
        t0 = time.perf_counter()
        hasil = mesin.buat_rekomendasi(payload)
        hasil["waktu_proses_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return self.kirim_json(hasil)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/rekomendasi":
            return self.kirim_galat(405, "metode_salah", "Gunakan POST untuk /rekomendasi")
        if path == "/api/health":
            model_siap = os.path.exists(os.path.join(BASE, "model.joblib"))
            return self.kirim_json({"status": "ok", "model_siap": model_siap})
        if path == "/model/info":
            return self.kirim_json(mesin.baca_metrik())
        if path == "/api/zona":
            with open(os.path.join(FRONTEND, "data", "zona_peta.json"), encoding="utf-8") as f:
                return self.kirim_json(json.load(f))
        if path == "/":
            return self.kirim_berkas(os.path.join(FRONTEND, "index.html"))
        # berkas statis
        kandidat = os.path.normpath(os.path.join(FRONTEND, path.lstrip("/")))
        if kandidat.startswith(FRONTEND) and os.path.isfile(kandidat):
            return self.kirim_berkas(kandidat)
        return self.kirim_galat(404, "tidak_ada", "Berkas tidak ditemukan")

    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"PupukPintar berjalan di http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
