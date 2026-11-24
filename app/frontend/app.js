/* ============================================================
   PupukPintar, logika antarmuka
   Data pengguna (lahan, riwayat, verifikasi) tersimpan di localStorage.
   Rekomendasi dihitung oleh server lewat POST /rekomendasi.
   ============================================================ */
"use strict";

const $ = (pilih) => document.querySelector(pilih);
const $$ = (pilih) => Array.from(document.querySelectorAll(pilih));

/* ---------- penyimpanan ---------- */
const KUNCI = "pp_state_v1";

function stateBawaan() {
  return {
    consent: false,
    optoutModel: true,
    nama: "",
    lahan: [],      // {id, nama, sumber:'peta'|'uji', pH, n_persen, p_ppm, k_me100g, tekstur, luas_ha, zona}
    riwayat: [],    // {id, tanggal, lahanId, namaLahan, payload, hasil, statusVerifikasi:'menunggu'|'disetujui'|'koreksi', catatanPenyuluh}
  };
}

function bacaState() {
  try {
    const s = JSON.parse(localStorage.getItem(KUNCI));
    if (s && Array.isArray(s.lahan) && Array.isArray(s.riwayat)) return s;
  } catch (e) { /* state rusak -> mulai baru */ }
  return stateBawaan();
}

function simpanState(s) { localStorage.setItem(KUNCI, JSON.stringify(s)); }

let state = bacaState();
let lahanTerpilih = null;
let komoditasAktif = "Padi";
let hasilAktif = null;
let paketAktif = "standar";

/* ---------- util ---------- */
const formatRp = (n) => "Rp " + Number(n).toLocaleString("id-ID");
const desimal = (x, c = 1) => String(x).replace(".", ",");
const hariIni = () => new Date().toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
const idBaru = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

function toast(pesan, galat = false) {
  const t = $("#toast");
  t.textContent = pesan;
  t.className = "toast" + (galat ? " galat" : "");
  t.hidden = false;
  clearTimeout(t._w);
  t._w = setTimeout(() => { t.hidden = true; }, 2600);
}

function kelasChip(status) {
  const peta = {
    "Sangat Rendah": "chip-sr", "Rendah": "chip-r",
    "Sedang": "chip-s",
    "Tinggi": "chip-t", "Sangat Tinggi": "chip-st",
  };
  return peta[status] || "chip-s";
}

function musimSekarang() {
  const b = new Date().getMonth() + 1; // 1..12
  return (b >= 10 || b <= 3) ? "Hujan" : "Kemarau";
}

/* ---------- status hara di sisi klien (untuk chip lahan) ---------- */
const BATAS = {
  N: [0.10, 0.21, 0.40, 0.60],
  P: [5.0, 11.0, 26.0, 60.0],
  K: [0.10, 0.21, 0.41, 0.80],
};
const LABEL = ["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"];
function statusUnsur(nilai, batang) {
  for (let i = 0; i < 4; i++) if (nilai < batang[i]) return LABEL[i];
  return LABEL[4];
}

/* ---------- navigasi ---------- */
function bukaLayar(nama) {
  const bolehTanpaConsent = (nama === "splash");
  if (!bolehTanpaConsent && !state.consent) { nama = "splash"; }

  $$(".tampilan").forEach(v => { v.hidden = true; });
  const layar = $("#v-" + nama);
  if (!layar) return;

  const tanpaNav = (nama === "splash" || nama === "hasil" || nama === "tambah-lahan" || nama === "peta" || nama === "uji-tanah");
  $("#nav-bawah").style.display = tanpaNav ? "none" : "grid";
  layar.hidden = false;
  $("#layar").scrollTop = 0;

  $$(".nav-item").forEach(b => {
    const aktif = b.dataset.buka === nama;
    b.classList.toggle("aktif", aktif);
    b.setAttribute("aria-current", aktif ? "page" : "false");
  });

  if (nama === "beranda") renderBeranda();
  if (nama === "lahan") renderLahan();
  if (nama === "rekomendasi") siapkanRekomendasi();
  if (nama === "peta") muatPeta();
  if (nama === "riwayat") renderRiwayat();
  if (nama === "penyuluhan") renderVerifikasi();
  if (nama === "profil") renderProfil();
}

document.addEventListener("click", (e) => {
  const tombol = e.target.closest("[data-buka]");
  if (tombol) bukaLayar(tombol.dataset.buka);
});

/* ---------- splash ---------- */
function masuk() {
  if (!$("#cek-setuju").checked) {
    $("#galat-setuju").hidden = false;
    return;
  }
  $("#galat-setuju").hidden = true;
  state.consent = true;
  simpanState(state);
  toast("Selamat datang di PupukPintar");
  bukaLayar("beranda");
}
$("#tombol-masuk").addEventListener("click", masuk);
$("#tombol-daftar").addEventListener("click", masuk);

/* ---------- beranda ---------- */
function renderBeranda() {
  const musim = musimSekarang();
  $("#beranda-musim").textContent = musim === "Hujan"
    ? "Musim hujan, puncak Oktober sampai Maret. Waktu terbaik mulai rencana pupuk."
    : "Musim kemarau, April sampai September. Perhatikan jadwal siram saat memupuk.";
  $("#rk-musim").value = musim;

  const w = $("#beranda-lahan");
  if (state.lahan.length === 0) {
    w.innerHTML = `
      <p class="label-kecil">LAHAN ANDA</p>
      <div class="keadaan-kosong">
        Belum ada lahan terdaftar.<br>
        Daftarkan lahan lewat peta hara atau hasil uji tanah untuk mulai.
        <div style="margin-top:10px"><button class="tombol garis kecil" data-buka="tambah-lahan">Daftarkan lahan pertama</button></div>
      </div>`;
  } else {
    const l = state.lahan[0];
    w.innerHTML = `
      <p class="label-kecil">LAHAN ANDA</p>
      <button class="keliling-lahan" data-buka="lahan" style="width:100%">
        <span class="nama-lahan">${l.nama}</span>
        <span class="sumber-lahan">${l.sumber === "peta" ? "dari peta hara SAFRONS: " + (l.zona || "") : "dari uji tanah"}</span>
        <div>${chipHara(l)}</div>
        <p class="ph-lahan">pH ${desimal(l.pH)} · luas ${desimal(l.luas_ha)} ha</p>
      </button>`;
  }

  const t = $("#beranda-terbaru");
  const terakhir = state.riwayat[0];
  if (!terakhir) {
    t.innerHTML = "";
  } else {
    const h = terakhir.hasil;
    const angka = h.tampilkan_angka
      ? `N ${h.dosis_kg_ha.N} · P ${h.dosis_kg_ha.P} · K ${h.dosis_kg_ha.K} kg/ha`
      : "Angka tidak ditampilkan, lihat saran sistem";
    t.innerHTML = `
      <p class="label-kecil">REKOMENDASI TERAKHIR</p>
      <div class="baris-riwayat">
        <div class="kepala-riwayat">
          <strong>${terakhir.namaLahan}</strong>
          <span class="tanggal-riwayat">${terakhir.tanggal}</span>
        </div>
        <p class="isi-riwayat">${terakhir.payload.komoditas} · ${angka}</p>
        ${badgeVerifikasi(terakhir.statusVerifikasi)}
      </div>
      <button class="tombol garis kecil" data-buka="riwayat">Lihat semua riwayat</button>`;
  }
}

function chipHara(l) {
  const sN = statusUnsur(l.n_persen, BATAS.N);
  const sP = statusUnsur(l.p_ppm, BATAS.P);
  const sK = statusUnsur(l.k_me100g, BATAS.K);
  return `
    <span class="chip-hara ${kelasChip(sN)}">N ${sN}</span>
    <span class="chip-hara ${kelasChip(sP)}">P ${sP}</span>
    <span class="chip-hara ${kelasChip(sK)}">K ${sK}</span>`;
}

function badgeVerifikasi(status) {
  if (!status || status === "menunggu") return `<span class="status-verifikasi sv-menunggu">Menunggu verifikasi penyuluh</span>`;
  if (status === "disetujui") return `<span class="status-verifikasi sv-disetujui">Disetujui penyuluh</span>`;
  return `<span class="status-verifikasi sv-koreksi">Minta koreksi</span>`;
}

/* ---------- lahan saya ---------- */
function renderLahan() {
  const w = $("#daftar-lahan");
  if (state.lahan.length === 0) {
    w.innerHTML = `<div class="keadaan-kosong">Belum ada lahan. Ketuk Tambah di pojok kanan atas untuk mendaftarkan lahan pertama Anda.</div>`;
    return;
  }
  w.innerHTML = state.lahan.map(l => `
    <div class="baris-lahan" data-id="${l.id}">
      <button class="keliling-lahan" data-lihat="${l.id}">
        <span class="nama-lahan">${l.nama}</span>
        <span class="sumber-lahan">${l.sumber === "peta" ? "dari peta hara SAFRONS: " + (l.zona || "") : "dari uji tanah"}</span>
        <div>${chipHara(l)}</div>
        <p class="ph-lahan">pH ${desimal(l.pH)} · N ${desimal(l.n_persen, 2)} · P ${desimal(l.p_ppm)} ppm · K ${desimal(l.k_me100g, 2)} · ${l.tekstur} · luas ${desimal(l.luas_ha)} ha</p>
      </button>
      <div class="aksi-lahan">
        <button class="tombol utama kecil" data-pakai="${l.id}">Pakai</button>
        <button class="tombol bahaya kecil" data-hapus-lahan="${l.id}" aria-label="Hapus ${l.nama}">Hapus</button>
      </div>
    </div>`).join("");
}

$("#daftar-lahan").addEventListener("click", (e) => {
  const pakai = e.target.closest("[data-pakai]");
  if (pakai) {
    lahanTerpilih = pakai.dataset.pakai;
    bukaLayar("rekomendasi");
    return;
  }
  const hapus = e.target.closest("[data-hapus-lahan]");
  if (hapus) {
    const id = hapus.dataset.hapusLahan;
    state.lahan = state.lahan.filter(l => l.id !== id);
    state.riwayat = state.riwayat.filter(r => r.lahanId !== id);
    simpanState(state);
    toast("Lahan dihapus");
    renderLahan();
  }
});

/* ---------- peta hara SAFRONS (Leaflet) ---------- */
let petaL = null;          // objek L.map
let lapisanArea = null;    // L.geoJSON
let areaDipilih = null;    // layer yang sedang dipilih

async function muatPeta() {
  $("#peta-galat").hidden = true;
  if (petaL && lapisanArea) { return; }
  $("#peta-muat").hidden = false;
  try {
    const r = await fetch("/api/peta");
    if (!r.ok) throw new Error("gagal");
    const dataPeta = await r.json();
    siapkanPeta(dataPeta);
    $("#peta-muat").hidden = true;
  } catch (e) {
    $("#peta-muat").hidden = true;
    $("#peta-galat").hidden = false;
  }
}
$("#peta-coba-lagi").addEventListener("click", muatPeta);

function warnaArea(pH) {
  if (pH < 5.0) return "#E4B84C";  // masam
  if (pH < 5.5) return "#E9CC7A";  // agak masam
  if (pH < 6.0) return "#B9CF9E";  // setengah masam
  return "#7FB58A";                // netral ke subur
}

function siapkanPeta(dataPeta) {
  const wadah = $("#peta-leaflet");
  if (!petaL) {
    petaL = L.map(wadah, { attributionControl: true, zoomControl: true, tap: true });
    petaL.setView([-6.55, 106.78], 10);
    // basemap daring; bila luring, poligon tetap tampil di atas latar peta polos
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; OpenStreetMap",
    }).addTo(petaL);
  }
  setTimeout(() => petaL.invalidateSize(), 60);

  lapisanArea = L.geoJSON(dataPeta, {
    style: (fitur) => {
      const p = fitur.properties;
      if (p.nodata) return { color: "#9AA39C", weight: 1, fillOpacity: 0.25, fillColor: "#CDD4CC", dashArray: "3 3" };
      return { color: "#FFFFFF", weight: 1.2, fillOpacity: 0.78, fillColor: warnaArea(p.pH) };
    },
    onEachFeature: (fitur, layer) => {
      const p = fitur.properties;
      layer.bindTooltip(p.nodata ? p.nama + " (tanpa data)" : p.nama, { sticky: true, direction: "top" });
      layer.on("click", () => pilihArea(p, layer));
    },
  }).addTo(petaL);
  petaL.fitBounds(lapisanArea.getBounds(), { padding: [10, 10] });
}

function pilihArea(p, layer) {
  if (p.nodata) {
    toast("Area \"" + p.nama + "\" tidak punya data hara sehingga tidak bisa dipilih.", true);
    return;
  }
  if (areaDipilih) areaDipilih.setStyle({ weight: 1.2, color: "#FFFFFF" });
  areaDipilih = layer;
  layer.setStyle({ weight: 3, color: "#143D2B" });
  layer.bringToFront();

  const w = $("#peta-detail");
  w.hidden = false;
  w.innerHTML = `
    <p class="label-kecil">AREA ${String(p.nama).toUpperCase()}</p>
    <p style="font-weight:800; color:var(--hijau-900); margin-bottom:6px">pH ${desimal(p.pH)} · N ${p.n_band} · P ${p.p_band} · K ${p.k_band} · ${p.tekstur}</p>
    <p class="teks-abu">Satuan unit lahan: ${p.unit || "-"}, lereng ${p.lereng || "-"} persen. Nilai pH rata-rata area SAFRONS. Band N, P, K hasil pembacaan peta dikonversi ke nilai uji tanah untuk model.</p>
    <div class="dua-kolom" style="margin-top:12px">
      <div class="medan">
        <label for="area-nama">Nama lahan Anda</label>
        <input id="area-nama" type="text" placeholder="contoh, Sawah ${p.nama}">
      </div>
      <div class="medan">
        <label for="area-luas">Luas (ha)</label>
        <input id="area-luas" type="number" step="0.05" min="0.05" max="10" value="0.75">
      </div>
    </div>
    <p id="galat-area" class="pesan-galat" hidden></p>
    <button class="tombol utama lebar" id="area-pakai">Gunakan Area Ini</button>`;
  $("#area-pakai").addEventListener("click", () => {
    const nama = $("#area-nama").value.trim();
    const luas = parseFloat($("#area-luas").value);
    const galat = [];
    if (!nama) galat.push("Isi nama lahan terlebih dahulu.");
    if (!(luas >= 0.05 && luas <= 10)) galat.push("Luas harus 0,05 sampai 10 ha.");
    if (galat.length) { const g = $("#galat-area"); g.textContent = galat.join(" "); g.hidden = false; return; }
    state.lahan.push({
      id: idBaru(), nama, sumber: "peta", zona: p.nama,
      pH: p.pH, n_persen: p.n_persen, p_ppm: p.p_ppm, k_me100g: p.k_me100g,
      tekstur: p.tekstur, luas_ha: luas,
    });
    simpanState(state);
    toast("Lahan \"" + nama + "\" terdaftar dari peta hara SAFRONS");
    bukaLayar("lahan");
  });
}

/* ---------- form uji tanah ---------- */
$("#form-uji-tanah").addEventListener("submit", (e) => {
  e.preventDefault();
  const g = $("#galat-uji-tanah");
  const nama = $("#ut-nama").value.trim();
  const pH = parseFloat($("#ut-ph").value);
  const n = parseFloat($("#ut-n").value);
  const p = parseFloat($("#ut-p").value);
  const k = parseFloat($("#ut-k").value);
  const tekstur = $("#ut-tekstur").value;
  const luas = parseFloat($("#ut-luas").value);

  const galat = [];
  if (!nama) galat.push("Isi nama lahan.");
  if (!(pH >= 3 && pH <= 9)) galat.push("pH harus di antara 3,0 dan 9,0.");
  if (!(n >= 0.01 && n <= 2)) galat.push("N (%) harus di antara 0,01 dan 2.");
  if (!(p >= 1 && p <= 200)) galat.push("P (ppm) harus di antara 1 dan 200.");
  if (!(k >= 0.01 && k <= 2.5)) galat.push("K (me/100g) harus di antara 0,01 dan 2,5.");
  if (!(luas >= 0.05 && luas <= 10)) galat.push("Luas harus 0,05 sampai 10 ha.");
  if (galat.length) { g.textContent = galat.join(" "); g.hidden = false; return; }
  g.hidden = true;

  state.lahan.push({
    id: idBaru(), nama, sumber: "uji", zona: null,
    pH, n_persen: n, p_ppm: p, k_me100g: k,
    tekstur, luas_ha: luas,
  });
  simpanState(state);
  toast("Hasil uji tanah tersimpan");
  bukaLayar("lahan");
});

/* ---------- rekomendasi ---------- */
function siapkanRekomendasi() {
  if (!lahanTerpilih && state.lahan.length > 0) lahanTerpilih = state.lahan[0].id;
  renderChipLahan();
  $("#catatan-hitung").hidden = false;
}

function renderChipLahan() {
  const w = $("#pilih-lahan");
  if (state.lahan.length === 0) {
    w.innerHTML = `<div class="keadaan-kosong" style="width:100%">Belum ada lahan. <button class="tautan" data-buka="tambah-lahan">Daftarkan lahan</button> terlebih dahulu.</div>`;
    $("#ringkasan-hara").textContent = "";
    return;
  }
  if (!lahanTerpilih || !state.lahan.find(l => l.id === lahanTerpilih)) {
    lahanTerpilih = state.lahan[0].id;
  }
  w.innerHTML = state.lahan.map(l =>
    `<button class="chip-lahan ${l.id === lahanTerpilih ? "aktif" : ""}" data-pilih-lahan="${l.id}" aria-pressed="${l.id === lahanTerpilih}">${l.nama}</button>`
  ).join("");
  tampilkanRingkasanHara();
}

$("#pilih-lahan").addEventListener("click", (e) => {
  const chip = e.target.closest("[data-pilih-lahan]");
  if (!chip) return;
  lahanTerpilih = chip.dataset.pilihLahan;
  renderChipLahan();
});

function tampilkanRingkasanHara() {
  const l = state.lahan.find(t => t.id === lahanTerpilih);
  if (!l) { $("#ringkasan-hara").textContent = ""; return; }
  $("#ringkasan-hara").innerHTML = `pH ${desimal(l.pH)} · N ${desimal(l.n_persen, 2)} · P ${desimal(l.p_ppm)} ppm · K ${desimal(l.k_me100g, 2)} · ${l.tekstur} · luas ${desimal(l.luas_ha)} ha` + (l.sumber === "uji" ? " (dari uji tanah)" : " (dari peta hara SAFRONS)");
  $("#rk-luas").value = l.luas_ha;
}

$$(".segmen[data-komoditas]").forEach(b => {
  b.addEventListener("click", () => {
    komoditasAktif = b.dataset.komoditas;
    $$(".segmen[data-komoditas]").forEach(t => {
      const aktif = t === b;
      t.classList.toggle("aktif", aktif);
      t.setAttribute("aria-pressed", String(aktif));
    });
    $("#rk-target").value = komoditasAktif === "Padi" ? 6 : 8;
  });
});

$("#tombol-hitung").addEventListener("click", async () => {
  const l = state.lahan.find(t => t.id === lahanTerpilih);
  const g = $("#galat-rekomendasi");
  if (!l) {
    g.textContent = "Pilih lahan terlebih dahulu, atau daftarkan lahan baru.";
    g.hidden = false;
    return;
  }
  const target = parseFloat($("#rk-target").value);
  const luas = parseFloat($("#rk-luas").value);
  const batasTarget = komoditasAktif === "Padi" ? [3, 10] : [3, 13];
  const galat = [];
  if (!(target >= batasTarget[0] && target <= batasTarget[1])) galat.push(`Target hasil ${komoditasAktif.toLowerCase()} harus ${desimal(batasTarget[0])} sampai ${desimal(batasTarget[1])} ton/ha.`);
  if (!(luas >= 0.05 && luas <= 10)) galat.push("Luas petak harus 0,05 sampai 10 ha.");
  if (galat.length) { g.textContent = galat.join(" "); g.hidden = false; return; }
  g.hidden = true;

  const payload = {
    pH: l.pH, n_persen: l.n_persen, p_ppm: l.p_ppm, k_me100g: l.k_me100g,
    tekstur: l.tekstur, komoditas: komoditasAktif,
    target_hasil_t_ha: target, luas_ha: luas,
    musim: $("#rk-musim").value,
  };

  $("#hitung-muat").hidden = false;
  $("#tombol-hitung").disabled = true;
  $("#catatan-hitung").hidden = true;
  try {
    const r = await fetch("/rekomendasi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (r.status === 422) {
      const d = await r.json();
      const pesan = (d.detail && d.detail.pesan ? d.detail.pesan : ["Input tidak layak"]).join(" ");
      lempar(pesan);
    }
    if (!r.ok) throw new Error("server");
    const hasil = await r.json();
    hasilAktif = { payload, hasil };
    tampilkanHasil();
    simpanRiwayat(payload, hasil);
    bukaLayar("hasil");
  } catch (err) {
    if (err && err.pesan) {
      g.textContent = err.pesan;
    } else {
      g.textContent = "Server tidak terjangkau. Periksa koneksi lalu coba lagi. Hasil yang pernah tersimpan tetap aman di riwayat.";
    }
    g.hidden = false;
  } finally {
    $("#hitung-muat").hidden = true;
    $("#tombol-hitung").disabled = false;
  }
});

function lempar(pesan) { const e = new Error("galat-input"); e.pesan = pesan; throw e; }

/* ---------- hasil ---------- */
function tampilkanHasil() {
  const { hasil } = hasilAktif;
  const badge = $("#badge-keyakinan");
  const persen = Math.round(hasil.keyakinan * 100);
  const kelas = hasil.kategori_keyakinan === "tinggi" ? "badge-tinggi" : hasil.kategori_keyakinan === "sedang" ? "badge-sedang" : "badge-rendah";
  const kata = hasil.kategori_keyakinan === "tinggi" ? "Yakin" : hasil.kategori_keyakinan === "sedang" ? "Cukup yakin" : "Tidak yakin";
  badge.textContent = `Keyakinan ${persen}% (${kata})`;
  badge.className = "badge-keyakinan " + kelas;

  const w = $("#isi-hasil");
  let isi = "";

  if (!hasil.tampilkan_angka) {
    isi += `
      <div class="kartu">
        <p class="label-kecil">MENGAPA ANGKA TIDAK DITAMPILKAN</p>
        <p style="font-size:14px">${hasil.peringatan[0]}</p>
        <p class="teks-abu" style="margin-top:8px">Rentang aman ${hasilAktif.payload.komoditas.toLowerCase()} menurut tabel resmi: N ${hasil.rentang_aman_kg_ha.N[0]} sampai ${hasil.rentang_aman_kg_ha.N[1]}, P ${hasil.rentang_aman_kg_ha.P[0]} sampai ${hasil.rentang_aman_kg_ha.P[1]}, K ${hasil.rentang_aman_kg_ha.K[0]} sampai ${hasil.rentang_aman_kg_ha.K[1]} kg/ha.</p>
      </div>`;
  } else {
    const d = hasil.dosis_kg_ha;
    const r = hasil.rentang_aman_kg_ha;
    isi += `
      <div class="tiga-dosis">
        <div class="kartu-dosis"><div class="unsur">N (UREA)</div><div class="angka">${d.N}</div><div class="satuan">kg/ha</div><div class="rentang">rentang ${r.N[0]} sampai ${r.N[1]}</div></div>
        <div class="kartu-dosis"><div class="unsur">P (SP-36)</div><div class="angka">${d.P}</div><div class="satuan">kg/ha</div><div class="rentang">rentang ${r.P[0]} sampai ${r.P[1]}</div></div>
        <div class="kartu-dosis"><div class="unsur">K (KCl)</div><div class="angka">${d.K}</div><div class="satuan">kg/ha</div><div class="rentang">rentang ${r.K[0]} sampai ${r.K[1]}</div></div>
      </div>

      <div class="kartu">
        <p class="label-kecil">KEBUTUHAN PUPUK PER PETAK (${desimal(hasilAktif.payload.luas_ha)} ha)</p>
        <div id="isi-kebutuhan"></div>
        <div class="baris-biaya"><span class="teks-abu">Estimasi biaya</span><span class="angka-biaya" id="angka-biaya"></span></div>
      </div>

      <div class="kartu">
        <p class="label-kecil">PAKET SESUAI MODAL</p>
        <div class="tersegmentasi tiga" id="segmen-paket" role="radiogroup" aria-label="Paket pemupukan">
          <button type="button" class="segmen ${paketAktif === "hemat" ? "aktif" : ""}" data-paket="hemat">Hemat</button>
          <button type="button" class="segmen ${paketAktif === "standar" ? "aktif" : ""}" data-paket="standar">Standar</button>
          <button type="button" class="segmen ${paketAktif === "optimal" ? "aktif" : ""}" data-paket="optimal">Optimal</button>
        </div>
        <p class="teks-abu" id="catatan-paket"></p>
      </div>`;
  }

  isi += `
      <div class="kartu">
        <p class="label-kecil">PENJELASAN SEDERHANA</p>
        <p style="font-size:14px">${hasil.penjelasan}</p>
        <div style="margin-top:8px">${chipHaraDariHasil(hasil.status_hara)}</div>
      </div>`;

  const daftarPeringatan = hasil.tampilkan_angka ? hasil.peringatan : hasil.peringatan.slice(1);
  if (daftarPeringatan.length > 0) {
    isi += daftarPeringatan.map(p => `
      <div class="peringatan-kotak">
        <svg viewBox="0 0 24 24" class="ikon" aria-hidden="true"><path d="M12 3 2.5 20h19L12 3Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M12 10v4m0 3v.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <span>${p}</span>
      </div>`).join("");
  }

  isi += `
      <div class="disclaimer-kotak">
        <svg viewBox="0 0 24 24" class="ikon" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 8h.01M12 11v5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <span>${hasil.disclaimer}</span>
      </div>
      <button class="tombol utama lebar" id="kirim-penyuluh">Kirim ke Penyuluh untuk Verifikasi</button>
      <button class="tombol garis lebar" data-buka="riwayat">Lihat Riwayat</button>`;

  w.innerHTML = isi;

  if (hasil.tampilkan_angka) {
    renderPaket(paketAktif);
    $("#segmen-paket").addEventListener("click", (e) => {
      const seg = e.target.closest("[data-paket]");
      if (!seg) return;
      paketAktif = seg.dataset.paket;
      $$("#segmen-paket .segmen").forEach(t => t.classList.toggle("aktif", t.dataset.paket === paketAktif));
      renderPaket(paketAktif);
    });
  }

  $("#kirim-penyuluh").addEventListener("click", kirimKePenyuluh);
}

function chipHaraDariHasil(status) {
  return `
    <span class="chip-hara ${kelasChip(status.N)}">N ${status.N}</span>
    <span class="chip-hara ${kelasChip(status.P)}">P ${status.P}</span>
    <span class="chip-hara ${kelasChip(status.K)}">K ${status.K}</span>`;
}

function renderPaket(nama) {
  const paket = hasilAktif.hasil.paket[nama];
  const keb = paket.kebutuhan_petak_kg;
  $("#isi-kebutuhan").innerHTML = `
    <table class="tabel-kebutuhan">
      <tr><td>Urea</td><td>${keb.Urea} kg</td></tr>
      <tr><td>SP-36</td><td>${keb.SP36} kg</td></tr>
      <tr><td>KCl</td><td>${keb.KCl} kg</td></tr>
    </table>`;
  $("#angka-biaya").textContent = formatRp(paket.estimasi_biaya_idr);
  $("#catatan-paket").textContent = paket.catatan;
}

function simpanRiwayat(payload, hasil) {
  const l = state.lahan.find(t => t.id === lahanTerpilih);
  state.riwayat.unshift({
    id: idBaru(),
    tanggal: hariIni(),
    lahanId: l ? l.id : null,
    namaLahan: l ? l.nama : "Lahan tanpa nama",
    payload, hasil,
    statusVerifikasi: "menunggu",
    catatanPenyuluh: "",
  });
  if (state.riwayat.length > 50) state.riwayat.pop();
  simpanState(state);
}

function kirimKePenyuluh() {
  const entri = state.riwayat.find(r => r.payload === hasilAktif.payload);
  if (entri) {
    entri.statusVerifikasi = "menunggu";
    simpanState(state);
  }
  toast("Rekomendasi dikirim ke penyuluh (mode demo, tersimpan di perangkat)");
  renderVerifikasi();
}

/* ---------- riwayat ---------- */
function renderRiwayat() {
  const w = $("#daftar-riwayat");
  if (state.riwayat.length === 0) {
    w.innerHTML = `<div class="keadaan-kosong">Belum ada rekomendasi tersimpan. Hasil perhitungan otomatis masuk ke sini.</div>`;
    return;
  }
  w.innerHTML = state.riwayat.map(r => {
    const h = r.hasil;
    const angka = h.tampilkan_angka
      ? `N ${h.dosis_kg_ha.N} · P ${h.dosis_kg_ha.P} · K ${h.dosis_kg_ha.K} kg/ha` + (h.estimasi_biaya_idr ? ` · ${formatRp(h.estimasi_biaya_idr)}` : "")
      : "Angka tidak ditampilkan oleh sistem";
    return `
      <div class="baris-riwayat">
        <div class="kepala-riwayat">
          <strong>${r.namaLahan}</strong>
          <span class="tanggal-riwayat">${r.tanggal}</span>
        </div>
        <p class="isi-riwayat">${r.payload.komoditas} · target ${desimal(r.payload.target_hasil_t_ha)} t/ha · ${angka}</p>
        ${badgeVerifikasi(r.statusVerifikasi)}
        ${r.catatanPenyuluh ? `<p class="teks-abu" style="margin-top:6px">Catatan penyuluh: ${r.catatanPenyuluh}</p>` : ""}
      </div>`;
  }).join("");
}

/* ---------- penyuluhan ---------- */
function renderVerifikasi() {
  const w = $("#daftar-verifikasi");
  const menunggu = state.riwayat.filter(r => r.statusVerifikasi === "menunggu");
  if (menunggu.length === 0) {
    w.innerHTML = `<div class="keadaan-kosong">Tidak ada permintaan verifikasi. Hasil yang dikirim ke penyuluh muncul di sini.</div>`;
    return;
  }
  w.innerHTML = `<div class="baris-verifikasi">` + menunggu.map(r => `
    <div class="baris-riwayat">
      <div class="kepala-riwayat">
        <strong>${r.namaLahan}</strong>
        <span class="tanggal-riwayat">${r.tanggal}</span>
      </div>
      <p class="isi-riwayat">${r.payload.komoditas} · N ${r.hasil.dosis_kg_ha ? r.hasil.dosis_kg_ha.N : "-"} · P ${r.hasil.dosis_kg_ha ? r.hasil.dosis_kg_ha.P : "-"} · K ${r.hasil.dosis_kg_ha ? r.hasil.dosis_kg_ha.K : "-"}</p>
      <div class="dua-kolom" style="margin-top:8px">
        <button class="tombol utama kecil" data-setujui="${r.id}">Setujui</button>
        <button class="tombol bahaya kecil" data-koreksi="${r.id}">Minta Koreksi</button>
      </div>
    </div>`).join("") + `</div>`;
}

$("#daftar-verifikasi").addEventListener("click", (e) => {
  const setuju = e.target.closest("[data-setujui]");
  const koreksi = e.target.closest("[data-koreksi]");
  if (setuju || koreksi) {
    const id = setuju ? setuju.dataset.setujui : koreksi.dataset.koreksi;
    const entri = state.riwayat.find(r => r.id === id);
    if (entri) {
      entri.statusVerifikasi = setuju ? "disetujui" : "koreksi";
      entri.catatanPenyuluh = setuju ? "" : "Ditinjau penyuluh pada demo, silakan sesuaikan di lapangan.";
      simpanState(state);
      toast(setuju ? "Rekomendasi disetujui" : "Diminta koreksi");
      renderVerifikasi();
    }
  }
});

/* ---------- profil ---------- */
function renderProfil() {
  $("#pf-nama").value = state.nama || "";
  $("#pf-optout").checked = !state.optoutModel;
  const w = $("#profil-model");
  fetch("/model/info").then(r => r.json()).then(m => {
    w.innerHTML = `
      <p>Model: Random Forest Regressor, dilatih dari ${Number(m.n_data).toLocaleString("id-ID")} baris data proxy tabel resmi.</p>
      <p>Agreement (rentang pakar, uji silang 5-fold): <strong>${String(m.cv.agreement_persen).replace(".", ",")}%</strong> · holdout 20%: <strong>${String(m.holdout.agreement_persen).replace(".", ",")}%</strong></p>
      <p>MAE: N ${m.cv.mae_kg.Dosis_N} · P ${m.cv.mae_kg.Dosis_P} · K ${m.cv.mae_kg.Dosis_K} kg/ha</p>`;
  }).catch(() => {
    w.textContent = "Metrik model tidak terjangkau saat ini.";
  });
}

$("#pf-nama").addEventListener("change", (e) => {
  state.nama = e.target.value.trim();
  simpanState(state);
  toast("Nama tersimpan");
});

$("#pf-optout").addEventListener("change", (e) => {
  state.optoutModel = !e.target.checked;
  simpanState(state);
  toast(e.target.checked ? "Data boleh dipakai memperbaiki model" : "Data tidak dipakai memperbaiki model (rekomendasi pribadi tetap jalan)");
});

$("#pf-hapus").addEventListener("click", () => {
  if (!confirm("Hapus semua lahan, riwayat, dan verifikasi di perangkat ini?")) return;
  state = stateBawaan();
  state.consent = true;
  simpanState(state);
  toast("Semua data Anda dihapus");
  bukaLayar("beranda");
});

/* ---------- status jaringan ---------- */
function perbaruiJaringan() {
  const el = $("#status-jaringan");
  const ok = navigator.onLine;
  el.textContent = ok ? "Online" : "Offline";
  el.className = "jaringan " + (ok ? "jaringan-ok" : "jaringan-gagal");
}
window.addEventListener("online", perbaruiJaringan);
window.addEventListener("offline", () => { perbaruiJaringan(); toast("Koneksi terputus. Coba hitung ulang setelah kembali.", true); });

/* ---------- mulai ---------- */
perbaruiJaringan();
bukaLayar(state.consent ? "beranda" : "splash");
