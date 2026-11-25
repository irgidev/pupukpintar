# -*- coding: utf-8 -*-
"""Entrypoint WSGI untuk Vercel: menyajikan antarmuka statis dan API rekomendasi.

Logika mesin diimpor dari model.py + konstanta.py (salinan mandiri di folder
ini, tanpa ketergantungan pandas maupun modul pelatihan data)."""

import json
import os
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from model import buat_rekomendasi, baca_metrik, validasi  # noqa: E402

FRONTEND = os.path.join(DIR, "frontend")
TIPE_MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def baca_berkas(jalur):
    with open(jalur, "rb") as f:
        return f.read()


def kirim_json(start_response, obj, status="200 OK"):
    isi = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    start_response(status, [("Content-Type", "application/json; charset=utf-8"), ("Content-Length", str(len(isi)))])
    return [isi]


def app(environ, start_response):
    metode = environ.get("REQUEST_METHOD", "GET")
    jalur = environ.get("PATH_INFO", "/").rstrip("/") or "/"

    if metode == "POST" and jalur == "/rekomendasi":
        try:
            panjang = int(environ.get("CONTENT_LENGTH") or 0)
            payload = json.loads(environ["wsgi.input"].read(panjang).decode("utf-8")) if panjang else {}
        except (ValueError, json.JSONDecodeError):
            return kirim_json(start_response, {"detail": {"jenis": "input_buruk", "pesan": ["Body bukan JSON yang sah"]}}, "400 Bad Request")
        galat = validasi(payload)
        if galat:
            return kirim_json(start_response, {"detail": {"jenis": "input_buruk", "pesan": galat}}, "422 Unprocessable Entity")
        return kirim_json(start_response, buat_rekomendasi(payload))

    if metode == "GET" and jalur == "/rekomendasi":
        return kirim_json(start_response, {"detail": "Gunakan POST untuk /rekomendasi"}, "405 Method Not Allowed")

    if metode == "GET" and jalur == "/model/info":
        return kirim_json(start_response, baca_metrik())

    if metode == "GET" and jalur == "/api/peta":
        with open(os.path.join(FRONTEND, "data", "peta_safrons.json"), encoding="utf-8") as f:
            return kirim_json(start_response, json.load(f))

    if metode == "GET" and jalur == "/api/health":
        return kirim_json(start_response, {"status": "ok", "model_siap": True})

    if metode == "GET":
        nama = "index.html" if jalur == "/" else jalur.lstrip("/")
        jalur_aman = os.path.normpath(os.path.join(FRONTEND, nama))
        if jalur_aman.startswith(FRONTEND) and os.path.isfile(jalur_aman):
            ekstensi = os.path.splitext(jalur_aman)[1].lower()
            tipe = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                    ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
                    ".svg": "image/svg+xml", ".png": "image/png"}.get(ekstensi, "application/octet-stream")
            isi = baca_berkas(jalur_aman)
            start_response("200 OK", [("Content-Type", tipe), ("Content-Length", str(len(isi)))])
            return [isi]
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Tidak ditemukan"]

    start_response("405 Method Not Allowed", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Metode tidak didukung"]
