# -*- coding: utf-8 -*-
"""Penyusun video demo PupukPintar: intro, teks penjelasan + panah, penutup.
Pendekatan tiga tahap (encode terpisah lalu concat demuxer) agar durasi
selalu terjaga."""

import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

import imageio_ffmpeg

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
FILM = os.path.join(ROOT, "video_demo", "PupukPintar_Demo_Kelompok14.mp4")
LOGO = os.path.normpath(os.path.join(ROOT, "..", "proyek_akhir", "Logo-IPB-baru1000.png"))

LBAR, LTING = 780, 1688
OFFSET_INTRO = 4.0
DURASI_INTRO = 4.0
DURASI_OUTRO = 3.5

HIJAU_TUA = (20, 61, 43)
KUNING = (242, 193, 78)
PUTIH = (255, 255, 255)
LATAR = (243, 244, 238)
ABU = (85, 99, 90)
NAVY_BESAR = (20, 44, 80)
TEKS_MUDA = (201, 211, 224)

F_TEBAL = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeuib.ttf")
F_REG = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeui.ttf")


def font(ukuran, tebal=True):
    return ImageFont.truetype(F_TEBAL if tebal else F_REG, ukuran)


def bungkus(draw, teks, f, lebar):
    kata = teks.split(" ")
    baris, kini = [], ""
    for k in kata:
        uji = (kini + " " + k).strip()
        if draw.textlength(uji, font=f) <= lebar:
            kini = uji
        else:
            if kini:
                baris.append(kini)
            kini = k
    if kini:
        baris.append(kini)
    return baris


def jalankan(perintah):
    open(os.path.join(DIR, 'cmd_terakhir.txt'), 'w').write(subprocess.list2cmdline(perintah))
    hasil = subprocess.run(perintah, capture_output=True, text=True)
    if hasil.returncode != 0:
        print(hasil.stderr[-1200:])
        raise SystemExit(1)


def kartu_pembuka():
    img = Image.new("RGB", (LBAR, LTING), LATAR)
    d = ImageDraw.Draw(img)
    if os.path.exists(LOGO):
        logo = Image.open(LOGO).convert("RGBA")
        logo = logo.resize((360, 360))
        img.paste(logo, (LBAR // 2 - 180, 140), logo)
    d.text((LBAR // 2, 540), "PupukPintar", font=font(96, True), fill=HIJAU_TUA, anchor="mm")
    d.text((LBAR // 2, 640), "Rekomendasi dosis pupuk N-P-K per lahan",
           font=font(34), fill=ABU, anchor="mm")
    d.line((LBAR // 2 - 180, 710, LBAR // 2 + 180, 710), fill=KUNING, width=8)
    d.text((LBAR // 2, 800), "VIDEO DEMO APLIKASI", font=font(40, True), fill=HIJAU_TUA, anchor="mm")
    d.text((LBAR // 2, 980), "Disusun Oleh Kelompok 14 | K1", font=font(44, True), fill=(29, 36, 31), anchor="mm")
    y = 1080
    for a in ["Irgi Setiawan - M0405241018", "Syarif Abdullah Assagaf - M0405241033",
              "Thogianna Anggitouli Metanoia Sinaga - M0405241077"]:
        d.text((LBAR // 2, y), a, font=font(30), fill=(29, 36, 31), anchor="mm")
        y += 62
    d.text((LBAR // 2, 1350), "PROGRAM STUDI KECERDASAN BUATAN", font=font(30, True), fill=HIJAU_TUA, anchor="mm")
    d.text((LBAR // 2, 1410), "SEKOLAH SAINS DATA MATEMATIKA DAN INFORMATIKA", font=font(24, True), fill=HIJAU_TUA, anchor="mm")
    d.text((LBAR // 2, 1470), "IPB UNIVERSITY  |  BOGOR  |  2026", font=font(26, True), fill=HIJAU_TUA, anchor="mm")
    return img


def kartu_penutup():
    img = Image.new("RGB", (LBAR, LTING), NAVY_BESAR)
    d = ImageDraw.Draw(img)
    d.text((LBAR // 2, 400), "Terima Kasih", font=font(96, True), fill=PUTIH, anchor="mm")
    d.text((LBAR // 2, 540), "PupukPintar: dosis pupuk yang tepat untuk lahan Anda,", font=font(32), fill=TEKS_MUDA, anchor="mm")
    d.text((LBAR // 2, 590), "bukan menebak dari kebiasaan tetangga", font=font(32), fill=TEKS_MUDA, anchor="mm")
    d.line((LBAR // 2 - 180, 680, LBAR // 2 + 180, 680), fill=KUNING, width=8)
    d.text((LBAR // 2, 760), "Kelompok 14 | K1", font=font(40, True), fill=PUTIH, anchor="mm")
    y = 880
    for a in ["Irgi Setiawan (M0405241018)", "Syarif Abdullah Assagaf (M0405241033)",
              "Thogianna A. M. Sinaga (M0405241077)"]:
        d.text((LBAR // 2, y), a, font=font(28), fill=TEKS_MUDA, anchor="mm")
        y += 56
    d.text((LBAR // 2, 1150), "pupukpintar.vercel.app  ·  github.com/irgidev/pupukpintar",
           font=font(24, True), fill=KUNING, anchor="mm")
    return img


def overlay_caption(teks, panah=None):
    img = Image.new("RGBA", (LBAR, LTING), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    margin = 36
    lebar_isi = LBAR - margin * 2 - 120  # ruang kanan untuk panah

    baris = bungkus(d, teks, font(30), lebar_isi - 24)
    tinggi_isi = len(baris) * 44 + 30
    kotak = (margin, 40, margin + lebar_isi, 40 + tinggi_isi)
    d.rounded_rectangle(kotak, radius=18, fill=(15, 40, 70, 228))
    d.rounded_rectangle(kotak, radius=18, outline=(242, 193, 78, 255), width=3)

    y = kotak[1] + 18
    for b in baris:
        d.text((margin + 22, y), b, font=font(30, True), fill=PUTIH)
        y += 44

    if panah:
        tx, ty = panah
        sx, sy = kotak[2] - 40, kotak[3] + 8
        d.line((sx, sy, tx, ty), fill=(242, 193, 78, 255), width=10)
        arah = 1 if ty >= sy else -1
        d.polygon([(tx, ty + arah * 34), (tx - 26, ty - arah * 4), (tx + 26, ty - arah * 4)],
                  fill=(242, 193, 78, 255))
    return img


def main():
    with open(os.path.join(DIR, "timeline.json"), encoding="utf-8") as f:
        timeline = json.load(f)

    ff = imageio_ffmpeg.get_ffmpeg_exe()

    kartu_pembuka().save(os.path.join(DIR, "intro.png"))
    kartu_penutup().save(os.path.join(DIR, "outro.png"))

    webm = max(
        (os.path.join(DIR, n) for n in os.listdir(DIR) if n.endswith(".webm")),
        key=os.path.getmtime,
    )
    assert os.path.exists(webm), "berkas webm perekaman tidak ditemukan"

    # 1) intro
    jalankan([ff, "-y", "-loop", "1", "-i", os.path.join(DIR, "intro.png"), "-t", str(DURASI_INTRO),
              "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(DIR, "seg_intro.mp4")])

    # 2) utama: overlay caption dikelompokkan agar jendela waktu tumpang-tindih
    #    ditangani dalam satu grafik overlay
    kelompok = []
    kini = None
    for entri in timeline:
        t1 = OFFSET_INTRO + entri["mulai"]
        t2 = t1 + entri["durasi"] + 0.4
        if kini is None or t1 > kini["akhir"]:
            kini = {"awal": t1, "akhir": t2, "caps": [entri]}
            kelompok.append(kini)
        else:
            kini["akhir"] = max(kini["akhir"], t2)
            kini["caps"].append(entri)

    segmen_utama = []
    for urut, k in enumerate(kelompok, start=1):
        keluar_seg = os.path.join(DIR, "seg_main_%02d.mp4" % urut)
        masukan = ["-i", webm]
        rantai = ["[0:v]scale=%d:%d,fps=30,setpts=PTS-STARTPTS[b01]" % (LBAR, LTING)]
        label = "b01"
        for j, entri in enumerate(k["caps"]):
            t1 = OFFSET_INTRO + entri["mulai"]
            t2 = OFFSET_INTRO + entri["mulai"] + entri["durasi"] + 0.4
            png = os.path.join(DIR, "cap_%02d_%02d.png" % (urut, j + 1))
            overlay_caption(entri["teks"], entri.get("panah")).save(png)
            masukan += ["-i", png]
            label_baru = "b%02d" % (len(k["caps"]) + 2 + j)
            rantai.append("[%s][%d:v]overlay=x=0:y=0:enable='between(t,%.2f,%.2f)'[%s]"
                          % (label, 1 + j, t1, t2, label_baru))
            label = label_baru
        rantai.append("[%s]format=yuv420p[v]" % label)
        jalankan([ff, "-y", *masukan, "-filter_complex", ";".join(rantai),
                  "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                  "-pix_fmt", "yuv420p", keluar_seg])
        segmen_utama.append(keluar_seg)

    # 3) outro
    jalankan([ff, "-y", "-loop", "1", "-i", os.path.join(DIR, "outro.png"), "-t", str(DURASI_OUTRO),
              "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(DIR, "seg_outro.mp4")])

    # 4) gabung dengan concat demuxer (re-encode ringan agar timebase seragam)
    daftar = os.path.join(DIR, "daftar_gabung.txt")
    with open(daftar, "w", encoding="utf-8") as f:
        f.write("file " + os.path.abspath(os.path.join(DIR, "seg_intro.mp4")).replace("\\", "/") + "\n")
        for seg in segmen_utama:
            f.write("file " + os.path.abspath(seg).replace("\\", "/") + "\n")
        f.write("file " + os.path.abspath(os.path.join(DIR, "seg_outro.mp4")).replace("\\", "/") + "\n")
    jalankan([ff, "-y", "-f", "concat", "-safe", "0", "-i", daftar,
              "-c:v", "libx264", "-preset", "medium", "-crf", "23",
              "-pix_fmt", "yuv420p", "-movflags", "+faststart", FILM])

    print("video final:", FILM, "| ukuran:", round(os.path.getsize(FILM) / 1048576, 1), "MB")


if __name__ == "__main__":
    main()
