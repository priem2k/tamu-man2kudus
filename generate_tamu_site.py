import os
import json
import datetime

OUTPUT_DIR = "public"

# Jika Anda sudah men-deploy Google Apps Script (File 1), Anda bisa menempelkan URL Web App-nya di bawah ini,
# ATAU langsung memasukkannya melalui menu tombol "Pengaturan API / Login Petugas" di halaman website!
DEFAULT_GAS_API_URL = os.environ.get("GAS_API_URL", "")

def build_manifest():
    manifest = {
        "name": "Siapa Tamu Hari Ini! — MAN 2 Kudus",
        "short_name": "Tamu MAN 2 Kudus",
        "description": "Sistem Informasi Jadwal & Penyambutan Tamu Eksternal MAN 2 Kudus",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#E5E7EB",
        "theme_color": "#065F46"
    }
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def build_index_html():
    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Siapa Tamu Hari Ini! — MAN 2 Kudus (Front Office & Informasi Warga Madrasah)</title>
    <meta name="description" content="Display daftar tamu harian, lokasi penyambutan, PIC pendamping, dan agenda kegiatan tamu eksternal di MAN 2 Kudus.">
    <link rel="manifest" href="./manifest.json">
    <meta name="theme-color" content="#065F46">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        @keyframes marquee {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
        .animate-marquee {{
            display: inline-block;
            white-space: nowrap;
            animation: marquee 32s linear infinite;
        }}
        .animate-marquee:hover {{
            animation-play-state: paused;
        }}
        @keyframes pulse-ring {{
            0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}
        .card-active-glow {{
            animation: pulse-ring 2.2s infinite;
        }}
        /* Mode Layar TV Front Office (Kiosk Dark Emerald Mode) */
        body.tv-kiosk-mode {{
            background-color: #06281E !important;
            color: #F8FAFC !important;
        }}
        body.tv-kiosk-mode .hide-on-tv {{
            display: none !important;
        }}
        body.tv-kiosk-mode .tv-card {{
            background-color: #0F392B !important;
            border-color: #10B981 !important;
            color: #F8FAFC !important;
        }}
        body.tv-kiosk-mode .tv-subbox {{
            background-color: #06281E !important;
            border-color: #047857 !important;
            color: #E2E8F0 !important;
        }}
        body.tv-kiosk-mode .tv-text-light {{
            color: #F8FAFC !important;
        }}
        body.tv-kiosk-mode .tv-text-muted {{
            color: #A7F3D0 !important;
        }}
    </style>
</head>
<body class="bg-gray-200 text-gray-900 min-h-screen flex flex-col justify-between selection:bg-emerald-700 selection:text-white transition-colors duration-300">

    <!-- TOP HEADER MADRASAH -->
    <header class="bg-gradient-to-r from-emerald-900 via-emerald-800 to-emerald-900 text-white shadow-lg border-b-4 border-amber-500 sticky top-0 z-30">
        <div class="max-w-7xl mx-auto px-4 py-3.5 flex flex-wrap items-center justify-between gap-4">
            <!-- Identitas MAN 2 Kudus -->
            <div class="flex items-center gap-3.5">
                <div class="w-12 h-12 rounded-2xl bg-amber-500 text-emerald-950 flex flex-col items-center justify-center font-black shadow-md shrink-0 border-2 border-amber-300">
                    <span class="text-xs leading-none">MAN 2</span>
                    <span class="text-[10px] font-extrabold tracking-wider">KUDUS</span>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <span class="bg-amber-400 text-emerald-950 text-[10px] font-black uppercase px-2 py-0.5 rounded-md tracking-wider">PTSP & HUMAS</span>
                        <span id="syncBadge" class="text-[11px] text-emerald-200 font-medium flex items-center gap-1">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Live Display
                        </span>
                    </div>
                    <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight leading-tight mt-0.5">Siapa Tamu Hari Ini!</h1>
                    <p id="subJudulHeader" class="text-xs text-emerald-200 font-medium">MAN 2 Kudus — Informasi Jadwal & Penyambutan Tamu Eksternal</p>
                </div>
            </div>

            <!-- Jam Digital Live & Tombol Mode TV / Petugas -->
            <div class="flex flex-wrap items-center gap-3 ml-auto">
                <div class="bg-emerald-950/80 border border-emerald-600/60 rounded-xl px-3.5 py-2 text-right">
                    <div id="liveClock" class="text-lg sm:text-xl font-black font-mono text-amber-400 leading-none">00:00:00 WIB</div>
                    <div id="liveDate" class="text-[11px] text-emerald-200 font-semibold mt-0.5">Memuat Tanggal...</div>
                </div>

                <button onclick="toggleTvMode()" id="btnTvMode"
                        class="bg-amber-500 hover:bg-amber-400 text-emerald-950 font-extrabold text-xs sm:text-sm px-3.5 py-2.5 rounded-xl shadow transition flex items-center gap-1.5 cursor-pointer">
                    <span>📺</span> <span id="tvBtnLabel">Mode TV Front Office</span>
                </button>

                <button onclick="openAdminModal()" id="btnAdminPanel"
                        class="hide-on-tv bg-emerald-700 hover:bg-emerald-600 text-white border border-emerald-500 font-bold text-xs sm:text-sm px-3.5 py-2.5 rounded-xl shadow transition flex items-center gap-1.5 cursor-pointer">
                    <span>🔐</span> <span id="adminBtnLabel">Petugas FO / Humas</span>
                </button>
            </div>
        </div>
    </header>

    <!-- MAIN CONTENT CONTAINER -->
    <main class="max-w-7xl w-full mx-auto px-4 py-6 space-y-6 flex-1">

        <!-- BARIS STATISTIK RINGKAS (SUMMARY CARDS) -->
        <section class="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
            <div class="tv-card bg-gray-100 border-2 border-gray-300 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                <div>
                    <span class="tv-text-muted text-xs font-bold uppercase tracking-wider text-gray-600 block">Total Tamu (Filter)</span>
                    <span id="statTotal" class="tv-text-light text-2xl sm:text-3xl font-black text-gray-900 mt-0.5 block">0</span>
                </div>
                <div class="w-11 h-11 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-xl font-bold">👥</div>
            </div>

            <div class="tv-card bg-gray-100 border-2 border-emerald-500 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                <div>
                    <span class="tv-text-muted text-xs font-bold uppercase tracking-wider text-emerald-800 block">Sedang Hadir / Disambut</span>
                    <span id="statHadir" class="tv-text-light text-2xl sm:text-3xl font-black text-emerald-700 mt-0.5 block">0</span>
                </div>
                <div class="w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center text-xl font-bold animate-pulse">🟢</div>
            </div>

            <div class="tv-card bg-gray-100 border-2 border-amber-400 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                <div>
                    <span class="tv-text-muted text-xs font-bold uppercase tracking-wider text-amber-800 block">Terjadwal Akan Hadir</span>
                    <span id="statAkan" class="tv-text-light text-2xl sm:text-3xl font-black text-amber-700 mt-0.5 block">0</span>
                </div>
                <div class="w-11 h-11 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center text-xl font-bold">🕒</div>
            </div>

            <div class="tv-card bg-gray-100 border-2 border-gray-300 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                <div>
                    <span class="tv-text-muted text-xs font-bold uppercase tracking-wider text-gray-600 block">Total Personel Tamu</span>
                    <span id="statOrang" class="tv-text-light text-2xl sm:text-3xl font-black text-blue-800 mt-0.5 block">0 Org</span>
                </div>
                <div class="w-11 h-11 rounded-xl bg-blue-100 text-blue-800 flex items-center justify-center text-xl font-bold">🏛️</div>
            </div>
        </section>

        <!-- NAVIGASI FILTER TANGGAL & PENCARIAN (SEMBUNYI SAAT MODE TV FULLSCREEN) -->
        <section class="hide-on-tv bg-gray-100 border-2 border-gray-300 rounded-2xl p-4 shadow-sm space-y-4">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <!-- Tombol Pintas Tanggal -->
                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="setDateFilter('YESTERDAY')" id="tabYesterday"
                            class="date-tab px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold border border-gray-300 bg-gray-200 text-gray-800 hover:bg-gray-300 transition cursor-pointer">
                        &larr; Kemarin
                    </button>
                    <button onclick="setDateFilter('TODAY')" id="tabToday"
                            class="date-tab px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold border-2 border-emerald-700 bg-emerald-700 text-white shadow-sm transition cursor-pointer">
                        📅 Hari Ini
                    </button>
                    <button onclick="setDateFilter('TOMORROW')" id="tabTomorrow"
                            class="date-tab px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold border border-gray-300 bg-gray-200 text-gray-800 hover:bg-gray-300 transition cursor-pointer">
                        Besok &rarr;
                    </button>
                    <button onclick="setDateFilter('UPCOMING')" id="tabUpcoming"
                            class="date-tab px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold border border-gray-300 bg-gray-200 text-gray-800 hover:bg-gray-300 transition cursor-pointer">
                        Semua Jadwal
                    </button>

                    <div class="flex items-center gap-1.5 bg-gray-200 border border-gray-400 rounded-xl px-3 py-1.5">
                        <span class="text-xs font-bold text-gray-700">Pilih Tgl:</span>
                        <input type="date" id="customDatePicker" onchange="setDateFilter('CUSTOM', this.value)"
                               class="bg-transparent text-xs sm:text-sm font-bold text-gray-900 focus:outline-none cursor-pointer">
                    </div>
                </div>

                <!-- Pencarian Tamu / Instansi / Nama Guru PIC -->
                <div class="flex items-center gap-2 flex-1 max-w-md">
                    <div class="relative flex-1">
                        <input type="text" id="searchInput" oninput="renderGuestCards()"
                               placeholder="Cari nama tamu, instansi, ruangan, atau PIC..."
                               class="w-full bg-gray-200 border-2 border-gray-300 focus:border-emerald-700 rounded-xl pl-9 pr-4 py-2 text-xs sm:text-sm font-semibold text-gray-900 placeholder-gray-500 focus:outline-none">
                        <span class="absolute left-3 top-2.5 text-gray-500 text-sm">🔍</span>
                    </div>
                    <button onclick="refreshFromServer()" title="Sinkronkan Data Terbaru"
                            class="bg-gray-300 hover:bg-gray-400 text-gray-900 font-bold px-3 py-2 rounded-xl text-xs sm:text-sm transition cursor-pointer shrink-0">
                        🔄 Sync
                    </button>
                </div>
            </div>

            <!-- Bar Status Login Petugas Front Office (Tampil Saat Petugas Sudah Login) -->
            <div id="adminToolbar" class="hidden pt-3 border-t border-gray-300 flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                    <span class="bg-emerald-100 text-emerald-900 border border-emerald-400 text-xs font-extrabold px-3 py-1 rounded-full">
                        ✅ Mode Petugas Front Office / Humas Aktif
                    </span>
                    <span class="text-xs text-gray-600">Anda dapat menambah tamu baru atau klik tombol status pada kartu di bawah.</span>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <button onclick="openGuestFormModal()"
                            class="bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-xs sm:text-sm px-4 py-2 rounded-xl shadow transition cursor-pointer">
                        + Input Tamu Baru
                    </button>
                    <button onclick="openRunningTextModal()"
                            class="bg-amber-500 hover:bg-amber-600 text-emerald-950 font-extrabold text-xs px-3.5 py-2 rounded-xl transition cursor-pointer">
                        📢 Ubah Running Text TV
                    </button>
                    <button onclick="logoutAdmin()"
                            class="bg-rose-100 hover:bg-rose-200 text-rose-900 font-bold text-xs px-3 py-2 rounded-xl transition cursor-pointer">
                        Keluar Mode Petugas
                    </button>
                </div>
            </div>
        </section>

        <!-- HEADER JUDUL TANGGAL AKTIF -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b-2 border-gray-300 pb-2.5">
            <div>
                <h2 id="activeFilterTitle" class="tv-text-light text-lg sm:text-2xl font-extrabold text-gray-900">
                    Daftar Tamu Hari Ini
                </h2>
                <p id="activeFilterSubtitle" class="tv-text-muted text-xs sm:text-sm text-gray-600 font-medium">
                    Menampilkan jadwal kehadiran tamu, lokasi penyambutan, dan personal penyambut (PIC)
                </p>
            </div>
            <div class="flex items-center gap-3 text-xs font-bold">
                <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> Sedang Hadir</span>
                <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-amber-400 inline-block"></span> Akan Hadir</span>
                <span class="inline-flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-blue-500 inline-block"></span> Selesai</span>
            </div>
        </div>

        <!-- GRID DAFTAR KARTU TAMU -->
        <section id="guestGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <!-- Dirender dinamis oleh JavaScript -->
        </section>

    </main>

    <!-- RUNNING TEXT (MARQUEE) KHUSUS FRONT OFFICE & FOOTER -->
    <div class="sticky bottom-0 z-20 mt-8">
        <div class="bg-emerald-950 text-amber-300 border-t-2 border-amber-500 py-2.5 px-4 overflow-hidden flex items-center">
            <span class="bg-amber-500 text-emerald-950 font-black text-[11px] uppercase px-2.5 py-0.5 rounded mr-3 shrink-0 z-10 shadow">
                INFO HUMAS
            </span>
            <div class="overflow-hidden whitespace-nowrap w-full">
                <p id="runningTextDisplay" class="animate-marquee text-xs sm:text-sm font-bold tracking-wide">
                    Selamat Datang di MAN 2 Kudus (Madrasah Akademik & Riset) — Zona Integritas Menuju Wilayah Bebas dari Korupsi (WBK). Mohon kesediaan Bapak/Ibu Tamu untuk melapor pada petugas Front Office / PTSP.
                </p>
            </div>
        </div>
        <footer class="hide-on-tv bg-gray-300 border-t border-gray-400 py-3 px-4 text-center text-xs text-gray-700 font-medium">
            <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
                <span><strong>Siapa Tamu Hari Ini!</strong> — Sistem Informasi Kehumasan & PTSP <strong>MAN 2 Kudus</strong></span>
                <span>Akses Cepat Mobile (HP Guru) & Display Layar Front Office</span>
            </div>
        </footer>
    </div>

    <!-- ===================================================================== -->
    <!-- MODAL 1: LOGIN PIN PETUGAS FRONT OFFICE / HUMAS & KONEKSI API         -->
    <!-- ===================================================================== -->
    <div id="adminLoginModal" class="fixed inset-0 bg-gray-900/75 hidden items-center justify-center z-50 p-4">
        <div class="bg-gray-100 border-2 border-gray-300 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5">
            <div class="flex items-center justify-between border-b border-gray-300 pb-3">
                <div>
                    <span class="text-[11px] font-extrabold uppercase tracking-wider text-emerald-800">Akses Petugas PTSP & Humas</span>
                    <h3 class="text-lg font-extrabold text-gray-900">Login Panel Petugas</h3>
                </div>
                <button onclick="closeAdminModal()" class="text-gray-500 hover:text-gray-900 font-black text-lg cursor-pointer">&times;</button>
            </div>

            <form onsubmit="handleAdminLogin(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-extrabold uppercase text-gray-700 mb-1">Masukkan PIN Petugas / Waka Humas</label>
                    <input type="password" id="pinInput" placeholder="Masukkan PIN (Default: man2kudus)" required
                           class="w-full bg-gray-200 border-2 border-gray-400 rounded-xl px-4 py-2.5 text-sm font-bold text-gray-900 focus:outline-none focus:border-emerald-700">
                    <span class="text-[11px] text-gray-600 mt-1 block">PIN default demo: <code class="bg-gray-300 px-1.5 py-0.5 rounded font-mono font-bold">man2kudus</code></span>
                </div>

                <div class="pt-2 border-t border-gray-300">
                    <label class="block text-xs font-bold text-gray-700 mb-1">URL Web App Google Spreadsheet (Opsional)</label>
                    <input type="url" id="gasUrlInput" placeholder="https://script.google.com/macros/s/.../exec"
                           class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-xs font-mono text-gray-800 focus:outline-none focus:border-emerald-700">
                    <span class="text-[11px] text-gray-500 mt-1 block">Jika dikosongkan, aplikasi tetap berjalan lancar menggunakan penyimpanan lokal browser.</span>
                </div>

                <div class="flex gap-2.5 pt-2">
                    <button type="button" onclick="closeAdminModal()"
                            class="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold text-xs py-2.5 rounded-xl transition cursor-pointer">
                        Batal
                    </button>
                    <button type="submit"
                            class="flex-1 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-xs py-2.5 rounded-xl shadow transition cursor-pointer">
                        Buka Panel Petugas &rarr;
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ===================================================================== -->
    <!-- MODAL 2: FORM INPUT / UPDATE DATA TAMU (PETUGAS FRONT OFFICE & HUMAS) -->
    <!-- ===================================================================== -->
    <div id="guestFormModal" class="fixed inset-0 bg-gray-900/75 hidden items-center justify-center z-50 p-4 overflow-y-auto">
        <div class="bg-gray-100 border-2 border-gray-300 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 my-8">
            <div class="flex items-center justify-between border-b border-gray-300 pb-3">
                <div>
                    <span class="text-[11px] font-extrabold uppercase tracking-wider text-emerald-800">Formulir Front Office / Humas MAN 2 Kudus</span>
                    <h3 id="formModalTitle" class="text-xl font-extrabold text-gray-900">Input Data Tamu Baru</h3>
                </div>
                <button onclick="closeGuestFormModal()" class="text-gray-500 hover:text-gray-900 font-black text-xl cursor-pointer">&times;</button>
            </div>

            <form onsubmit="handleSaveGuest(event)" class="space-y-4">
                <input type="hidden" id="fIdTamu">

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Tanggal Kehadiran *</label>
                        <input type="date" id="fTanggal" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3 py-2 text-sm font-bold text-gray-900">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Jam Mulai (WIB) *</label>
                        <input type="time" id="fWaktuMulai" value="08:30" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3 py-2 text-sm font-bold text-gray-900">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Jam Selesai (WIB) *</label>
                        <input type="time" id="fWaktuSelesai" value="10:30" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3 py-2 text-sm font-bold text-gray-900">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-12 gap-3.5">
                    <div class="sm:col-span-5">
                        <label class="block text-xs font-bold text-gray-800 mb-1">Nama Tamu / Pimpinan Rombongan *</label>
                        <input type="text" id="fNamaTamu" placeholder="Contoh: Drs. H. Ahmad Fauzi, M.Pd." required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                    </div>
                    <div class="sm:col-span-5">
                        <label class="block text-xs font-bold text-gray-800 mb-1">Instansi / Lembaga Asal *</label>
                        <input type="text" id="fInstansi" placeholder="Contoh: Kemenag Kudus / MAN 1 Malang" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                    </div>
                    <div class="sm:col-span-2">
                        <label class="block text-xs font-bold text-gray-800 mb-1">Jml Orang *</label>
                        <input type="number" id="fJumlahOrang" value="1" min="1" max="500" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3 py-2 text-sm font-bold text-gray-900">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">📍 Lokasi / Tempat Penyambutan Tamu *</label>
                        <input type="text" id="fLokasi" list="lokasiOptions" placeholder="Pilih atau ketik ruangan..." required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                        <datalist id="lokasiOptions"></datalist>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">👤 Nama Personal Penyambut (PIC) *</label>
                        <input type="text" id="fPic" list="picOptions" placeholder="Pilih atau ketik nama guru/pejabat..." required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                        <datalist id="picOptions"></datalist>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Kepentingan Tamu *</label>
                        <input type="text" id="fKepentingan" placeholder="Contoh: Studi Tiru Madrasah Riset" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Kegiatan yang Dilakukan *</label>
                        <input type="text" id="fKegiatan" placeholder="Contoh: Diskusi di Aula & Kunjungan Lab" required
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Status Kehadiran Tamu *</label>
                        <select id="fStatus" class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-bold text-gray-900">
                            <option value="Akan Hadir">🟡 Terjadwal / Akan Hadir</option>
                            <option value="Sedang Berlangsung">🟢 Sudah Hadir / Sedang Berlangsung</option>
                            <option value="Selesai">🔵 Kunjungan Selesai</option>
                            <option value="Batal">🔴 Dijadwalkan Ulang / Batal</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-800 mb-1">Diinput / Diupdate Oleh Petugas</label>
                        <input type="text" id="fPetugas" value="Petugas Front Office (PTSP)"
                               class="w-full bg-gray-200 border border-gray-400 rounded-xl px-3.5 py-2 text-sm font-semibold text-gray-900">
                    </div>
                </div>

                <div class="flex gap-3 pt-3 border-t border-gray-300">
                    <button type="button" onclick="closeGuestFormModal()"
                            class="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold text-sm py-2.5 rounded-xl transition cursor-pointer">
                        Batal
                    </button>
                    <button type="submit" id="btnSaveGuest"
                            class="flex-1 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-sm py-2.5 rounded-xl shadow transition cursor-pointer">
                        💾 Simpan Data Tamu
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ===================================================================== -->
    <!-- JAVASCRIPT ENGINE: STATE, FALLBACK DATA, FILTERING & API SYNC         -->
    <!-- ===================================================================== -->
    <script>
        const DEFAULT_API_URL = "{DEFAULT_GAS_API_URL}";
        let apiEndpoint = localStorage.getItem("MAN2_GAS_API_URL") || DEFAULT_API_URL;
        let adminPin = sessionStorage.getItem("MAN2_ADMIN_PIN") || "";
        let isAdminMode = Boolean(adminPin);
        let isTvMode = false;
        let currentFilterMode = "TODAY";
        let customFilterDate = "";

        // Helper format tanggal YYYY-MM-DD sesuai waktu lokal (WIB)
        function getOffsetDateStr(offsetDays = 0) {{
            const d = new Date();
            d.setDate(d.getDate() + offsetDays);
            const yyyy = d.getFullYear();
            const mm = String(d.getMonth() + 1).padStart(2, "0");
            const dd = String(d.getDate()).padStart(2, "0");
            return `${{yyyy}}-${{mm}}-${{dd}}`;
        }}

        // Data Awal Bawaan (Otomatis menyesuaikan tanggal Hari Ini, Kemarin & Besok)
        function getInitialFallbackData() {{
            const today = getOffsetDateStr(0);
            const yesterday = getOffsetDateStr(-1);
            const tomorrow = getOffsetDateStr(1);

            return {{
                config: {{
                    NAMA_INSTANSI: "MAN 2 KUDUS",
                    SUB_JUDUL: "Madrasah Akademik & Riset — Informasi Jadwal & Penyambutan Tamu",
                    RUNNING_TEXT: "Selamat Datang di MAN 2 Kudus (Madrasah Akademik & Riset) — Zona Integritas Menuju Wilayah Bebas dari Korupsi (WBK). Mohon kesediaan Bapak/Ibu Tamu untuk melapor pada petugas Front Office / PTSP."
                }},
                referensi: {{
                    lokasi: [
                        "Lobby PTSP / Ruang Tamu Front Office",
                        "Ruang Kepala Madrasah",
                        "Ruang Rapat Pimpinan (Meeting Room)",
                        "Auditorium / Aula MAN 2 Kudus",
                        "Ruang Waka / Humas",
                        "Laboratorium Riset / Sains Terpadu",
                        "Studio Podcast / Multimedia Humas"
                    ],
                    pic: [
                        "Waka Bidang Humas",
                        "Kepala MAN 2 Kudus",
                        "Kepala Urusan Tata Usaha (Ka. TU)",
                        "Waka Bidang Akademik / Kurikulum",
                        "Waka Bidang Kesiswaan",
                        "Waka Bidang Sarana Prasarana",
                        "Koordinator Riset & Akademik (BCS)",
                        "Koordinator BK & Kerjasama PTN"
                    ]
                }},
                guests: [
                    {{
                        id_tamu: "TM-001",
                        tanggal: today,
                        waktu_mulai: "08:00",
                        waktu_selesai: "10:00",
                        nama_tamu: "Bpk. H. Sholihin, S.Ag., M.Pd.I",
                        instansi: "Kemenag Kabupaten Kudus",
                        jumlah_orang: 2,
                        kepentingan: "Monitoring & Pembinaan Madrasah",
                        kegiatan: "Supervisi administrasi kehumasan, layanan PTSP & tinjauan program riset",
                        lokasi: "Ruang Kepala Madrasah",
                        pic_penyambut: "Kepala MAN 2 Kudus & Waka Humas",
                        status: "Sedang Berlangsung",
                        petugas_input: "Petugas PTSP Pagi"
                    }},
                    {{
                        id_tamu: "TM-002",
                        tanggal: today,
                        waktu_mulai: "09:30",
                        waktu_selesai: "12:00",
                        nama_tamu: "Drs. H. Ahmad Fauzi, M.Pd. & Rombongan",
                        instansi: "MAN 1 Pekanbaru",
                        jumlah_orang: 18,
                        kepentingan: "Studi Tiru Madrasah Akademik & Riset",
                        kegiatan: "Penyambutan di Auditorium, pemaparan manajemen BCS/Riset & tur laboratorium",
                        lokasi: "Auditorium / Aula MAN 2 Kudus",
                        pic_penyambut: "Waka Humas, Waka Kurikulum & Koordinator Riset",
                        status: "Akan Hadir",
                        petugas_input: "Waka Humas"
                    }},
                    {{
                        id_tamu: "TM-003",
                        tanggal: today,
                        waktu_mulai: "13:00",
                        waktu_selesai: "14:30",
                        nama_tamu: "Tim Humas & PMB Undip",
                        instansi: "Universitas Diponegoro (Undip) Semarang",
                        jumlah_orang: 4,
                        kepentingan: "Sosialisasi SNBP & SNBT 2027",
                        kegiatan: "Presentasi informasi kuota, beasiswa & jalur prestasi bagi siswa kelas XII",
                        lokasi: "Gedung Serbaguna / Aula Lantai 2",
                        pic_penyambut: "Waka Kurikulum & Koordinator BK",
                        status: "Akan Hadir",
                        petugas_input: "Petugas PTSP Pagi"
                    }},
                    {{
                        id_tamu: "TM-004",
                        tanggal: yesterday,
                        waktu_mulai: "09:00",
                        waktu_selesai: "11:00",
                        nama_tamu: "Komite Madrasah & Perwakilan Wali Murid",
                        instansi: "Pengurus Komite MAN 2 Kudus",
                        jumlah_orang: 6,
                        kepentingan: "Rapat Koordinasi Program Semester",
                        kegiatan: "Evaluasi program pendukung akademik & fasilitas riset siswa",
                        lokasi: "Ruang Rapat Pimpinan (Meeting Room)",
                        pic_penyambut: "Kepala Madrasah, Ka. TU & Para Waka",
                        status: "Selesai",
                        petugas_input: "Petugas PTSP"
                    }},
                    {{
                        id_tamu: "TM-005",
                        tanggal: tomorrow,
                        waktu_mulai: "08:30",
                        waktu_selesai: "11:30",
                        nama_tamu: "Kepala Madrasah & Tim Jurnalistik",
                        instansi: "MAN 2 Kota Malang",
                        jumlah_orang: 12,
                        kepentingan: "Benchmarking Kehumasan & Media Publikasi",
                        kegiatan: "Sharing session pengelolaan website madrasah, media sosial & studio podcast",
                        lokasi: "Ruang Rapat Pimpinan & Studio Humas",
                        pic_penyambut: "Waka Bidang Humas & Tim Media MAN 2 Kudus",
                        status: "Akan Hadir",
                        petugas_input: "Waka Humas"
                    }}
                ]
            }};
        }}

        let appState = (function() {{
            const saved = localStorage.getItem("MAN2_TAMU_STATE_V1");
            if (saved) {{
                try {{ return JSON.parse(saved); }} catch (e) {{}}
            }}
            return getInitialFallbackData();
        }})();

        function saveStateToLocal() {{
            localStorage.setItem("MAN2_TAMU_STATE_V1", JSON.stringify(appState));
        }}

        // Jam Digital Real-Time WIB
        function updateLiveClock() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString("id-ID", {{ hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }});
            const dateStr = now.toLocaleDateString("id-ID", {{ weekday: "long", day: "numeric", month: "long", year: "numeric" }});
            document.getElementById("liveClock").textContent = timeStr.replace(/\\./g, ":") + " WIB";
            document.getElementById("liveDate").textContent = dateStr;
        }}

        function formatReadableDate(yyyy_mm_dd) {{
            if (!yyyy_mm_dd) return "-";
            const parts = yyyy_mm_dd.split("-");
            if (parts.length !== 3) return yyyy_mm_dd;
            const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
            return d.toLocaleDateString("id-ID", {{ weekday: "long", day: "numeric", month: "long", year: "numeric" }});
        }}

        function populateDropdownLists() {{
            const lokEl = document.getElementById("lokasiOptions");
            const picEl = document.getElementById("picOptions");
            lokEl.innerHTML = (appState.referensi.lokasi || []).map(x => `<option value="${{x}}">`).join("");
            picEl.innerHTML = (appState.referensi.pic || []).map(x => `<option value="${{x}}">`).join("");
            if (appState.config && appState.config.RUNNING_TEXT) {{
                document.getElementById("runningTextDisplay").textContent = appState.config.RUNNING_TEXT;
            }}
        }}

        function setDateFilter(mode, customVal = "") {{
            currentFilterMode = mode;
            if (mode === "CUSTOM") {{
                customFilterDate = customVal;
            }} else {{
                document.getElementById("customDatePicker").value = "";
            }}

            const tabs = {{
                YESTERDAY: document.getElementById("tabYesterday"),
                TODAY: document.getElementById("tabToday"),
                TOMORROW: document.getElementById("tabTomorrow"),
                UPCOMING: document.getElementById("tabUpcoming")
            }};

            Object.keys(tabs).forEach(k => {{
                if (k === mode) {{
                    tabs[k].className = "date-tab px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold border-2 border-emerald-700 bg-emerald-700 text-white shadow-sm transition cursor-pointer";
                }} else {{
                    tabs[k].className = "date-tab px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold border border-gray-300 bg-gray-200 text-gray-800 hover:bg-gray-300 transition cursor-pointer";
                }}
            }});

            renderGuestCards();
        }}

        function getStatusBadgeHtml(status) {{
            if (status === "Sedang Berlangsung") {{
                return `<span class="inline-flex items-center gap-1.5 bg-emerald-100 text-emerald-900 border-2 border-emerald-500 text-xs font-extrabold px-3 py-1 rounded-full">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-ping"></span> Sedang Hadir / Disambut
                        </span>`;
            }}
            if (status === "Selesai") {{
                return `<span class="inline-flex items-center gap-1.5 bg-blue-100 text-blue-900 border border-blue-400 text-xs font-bold px-3 py-1 rounded-full">
                            🔵 Kunjungan Selesai
                        </span>`;
            }}
            if (status === "Batal") {{
                return `<span class="inline-flex items-center gap-1.5 bg-rose-100 text-rose-900 border border-rose-400 text-xs font-bold px-3 py-1 rounded-full">
                            🔴 Dijadwalkan Ulang / Batal
                        </span>`;
            }}
            return `<span class="inline-flex items-center gap-1.5 bg-amber-100 text-amber-950 border border-amber-400 text-xs font-extrabold px-3 py-1 rounded-full">
                        🟡 Terjadwal / Akan Hadir
                    </span>`;
        }}

        function renderGuestCards() {{
            const todayStr = getOffsetDateStr(0);
            const yestStr = getOffsetDateStr(-1);
            const tomStr = getOffsetDateStr(1);
            const query = (document.getElementById("searchInput").value || "").toLowerCase().trim();

            let targetDateLabel = "";
            let filtered = (appState.guests || []).filter(g => {{
                if (currentFilterMode === "TODAY") {{
                    targetDateLabel = "Daftar Tamu Hari Ini (" + formatReadableDate(todayStr) + ")";
                    return g.tanggal === todayStr;
                }}
                if (currentFilterMode === "YESTERDAY") {{
                    targetDateLabel = "Daftar Tamu Kemarin (" + formatReadableDate(yestStr) + ")";
                    return g.tanggal === yestStr;
                }}
                if (currentFilterMode === "TOMORROW") {{
                    targetDateLabel = "Daftar Tamu Besok (" + formatReadableDate(tomStr) + ")";
                    return g.tanggal === tomStr;
                }}
                if (currentFilterMode === "CUSTOM" && customFilterDate) {{
                    targetDateLabel = "Daftar Tamu Tanggal " + formatReadableDate(customFilterDate);
                    return g.tanggal === customFilterDate;
                }}
                targetDateLabel = "Seluruh Jadwal Tamu MAN 2 Kudus";
                return true;
            }});

            if (query) {{
                filtered = filtered.filter(g =>
                    (g.nama_tamu || "").toLowerCase().includes(query) ||
                    (g.instansi || "").toLowerCase().includes(query) ||
                    (g.lokasi || "").toLowerCase().includes(query) ||
                    (g.pic_penyambut || "").toLowerCase().includes(query) ||
                    (g.kepentingan || "").toLowerCase().includes(query) ||
                    (g.kegiatan || "").toLowerCase().includes(query)
                );
            }}

            // Urutkan berdasarkan Tanggal dan Jam Mulai
            filtered.sort((a, b) => {{
                const keyA = (a.tanggal || "") + " " + (a.waktu_mulai || "");
                const keyB = (b.tanggal || "") + " " + (b.waktu_mulai || "");
                return keyA.localeCompare(keyB);
            }});

            document.getElementById("activeFilterTitle").textContent = targetDateLabel;

            // Update Statistik
            const totalTamu = filtered.length;
            const sedangHadir = filtered.filter(g => g.status === "Sedang Berlangsung").length;
            const akanHadir = filtered.filter(g => g.status === "Akan Hadir").length;
            const totalOrang = filtered.reduce((acc, g) => acc + (Number(g.jumlah_orang) || 1), 0);

            document.getElementById("statTotal").textContent = totalTamu;
            document.getElementById("statHadir").textContent = sedangHadir;
            document.getElementById("statAkan").textContent = akanHadir;
            document.getElementById("statOrang").textContent = totalOrang + " Org";

            const grid = document.getElementById("guestGrid");
            if (filtered.length === 0) {{
                grid.innerHTML = `
                    <div class="tv-card col-span-full bg-gray-100 border-2 border-dashed border-gray-400 rounded-2xl p-10 text-center space-y-2">
                        <div class="text-4xl">🕌</div>
                        <h3 class="tv-text-light text-lg font-extrabold text-gray-900">Belum Ada Jadwal Tamu pada Tanggal / Filter Ini</h3>
                        <p class="tv-text-muted text-xs sm:text-sm text-gray-600 max-w-md mx-auto">
                            Silakan pilih tab tanggal lain (Kemarin / Besok / Semua Jadwal) atau klik tombol <strong>Petugas FO / Humas</strong> untuk menginput jadwal tamu baru.
                        </p>
                    </div>
                `;
                return;
            }}

            grid.innerHTML = filtered.map(g => {{
                const isLive = g.status === "Sedang Berlangsung";
                const borderClass = isLive
                    ? "border-2 border-emerald-600 card-active-glow"
                    : "border-2 border-gray-300";

                const adminControls = isAdminMode ? `
                    <div class="hide-on-tv pt-3 mt-3 border-t border-gray-300 flex flex-wrap items-center justify-between gap-2">
                        <div class="flex flex-wrap gap-1.5">
                            <button onclick="quickStatus('${{g.id_tamu}}', 'Sedang Berlangsung')"
                                    class="bg-emerald-700 hover:bg-emerald-800 text-white text-[11px] font-extrabold px-2.5 py-1.5 rounded-lg transition cursor-pointer">
                                🟢 Set Hadir
                            </button>
                            <button onclick="quickStatus('${{g.id_tamu}}', 'Selesai')"
                                    class="bg-blue-700 hover:bg-blue-800 text-white text-[11px] font-bold px-2.5 py-1.5 rounded-lg transition cursor-pointer">
                                🔵 Selesai
                            </button>
                        </div>
                        <div class="flex gap-1.5">
                            <button onclick="editGuest('${{g.id_tamu}}')"
                                    class="bg-gray-300 hover:bg-gray-400 text-gray-900 text-[11px] font-bold px-2.5 py-1.5 rounded-lg transition cursor-pointer">
                                ✏️ Edit
                            </button>
                            <button onclick="deleteGuest('${{g.id_tamu}}')"
                                    class="bg-rose-100 hover:bg-rose-200 text-rose-900 text-[11px] font-bold px-2.5 py-1.5 rounded-lg transition cursor-pointer">
                                🗑️
                            </button>
                        </div>
                    </div>
                ` : "";

                return `
                <article class="tv-card bg-gray-100 ${{borderClass}} rounded-2xl p-5 shadow-sm flex flex-col justify-between transition hover:shadow-md">
                    <div class="space-y-3.5">
                        <!-- Baris Atas: Jam & Status -->
                        <div class="flex flex-wrap items-center justify-between gap-2">
                            <div class="bg-emerald-900 text-amber-300 font-mono font-black text-xs sm:text-sm px-3 py-1 rounded-lg shadow-sm">
                                🕒 ${{g.waktu_mulai}} - ${{g.waktu_selesai}} WIB
                            </div>
                            ${{getStatusBadgeHtml(g.status)}}
                        </div>

                        <!-- Tanggal & Jumlah Rombongan -->
                        <div class="flex items-center justify-between text-xs font-bold text-gray-600 tv-text-muted">
                            <span>📅 ${{formatReadableDate(g.tanggal)}}</span>
                            <span class="bg-gray-200 text-gray-900 border border-gray-300 px-2.5 py-0.5 rounded-full font-extrabold">
                                👥 ${{g.jumlah_orang}} Orang
                            </span>
                        </div>

                        <!-- Nama Tamu & Instansi -->
                        <div>
                            <span class="text-[11px] font-extrabold uppercase tracking-wider text-emerald-800 tv-text-muted block">
                                ${{g.instansi}}
                            </span>
                            <h3 class="tv-text-light text-lg sm:text-xl font-extrabold text-gray-900 leading-snug mt-0.5">
                                ${{g.nama_tamu}}
                            </h3>
                        </div>

                        <!-- Kotak Kepentingan & Kegiatan -->
                        <div class="tv-subbox bg-gray-200/90 border border-gray-300 rounded-xl p-3 space-y-1">
                            <div class="text-xs font-extrabold text-gray-900 tv-text-light">
                                🎯 Kepentingan: <span class="text-emerald-900 tv-text-muted">${{g.kepentingan}}</span>
                            </div>
                            <p class="text-xs text-gray-700 tv-text-light leading-relaxed">
                                📋 <strong>Kegiatan:</strong> ${{g.kegiatan}}
                            </p>
                        </div>
                    </div>

                    <!-- Highlight Lokasi Penyambutan & PIC Penyambut -->
                    <div class="mt-4 pt-3 border-t border-gray-300 space-y-2">
                        <div class="bg-emerald-50 border border-emerald-300 rounded-xl p-2.5 flex items-start gap-2.5">
                            <span class="text-base leading-none mt-0.5">📍</span>
                            <div class="text-xs">
                                <span class="text-emerald-900 font-bold block uppercase text-[10px] tracking-wider">Lokasi / Tempat Penyambutan:</span>
                                <strong class="text-emerald-950 text-xs sm:text-sm font-extrabold">${{g.lokasi}}</strong>
                            </div>
                        </div>

                        <div class="bg-amber-50 border border-amber-300 rounded-xl p-2.5 flex items-start gap-2.5">
                            <span class="text-base leading-none mt-0.5">👤</span>
                            <div class="text-xs">
                                <span class="text-amber-900 font-bold block uppercase text-[10px] tracking-wider">Penanggung Jawab Menyambut (PIC):</span>
                                <strong class="text-gray-950 text-xs sm:text-sm font-extrabold">${{g.pic_penyambut}}</strong>
                            </div>
                        </div>

                        ${{adminControls}}
                    </div>
                </article>
                `;
            }}).join("");
        }}

        // Toggle Mode Layar TV Front Office (Fullscreen + Dark Emerald Theme)
        function toggleTvMode() {{
            isTvMode = !isTvMode;
            const body = document.body;
            const label = document.getElementById("tvBtnLabel");
            if (isTvMode) {{
                body.classList.add("tv-kiosk-mode");
                label.textContent = "Keluar Mode TV";
                setDateFilter("TODAY");
                if (document.documentElement.requestFullscreen) {{
                    document.documentElement.requestFullscreen().catch(() => {{}});
                }}
            }} else {{
                body.classList.remove("tv-kiosk-mode");
                label.textContent = "Mode TV Front Office";
                if (document.fullscreenElement && document.exitFullscreen) {{
                    document.exitFullscreen().catch(() => {{}});
                }}
            }}
        }}

        // Modal Login Admin / Petugas FO
        function openAdminModal() {{
            if (isAdminMode) {{
                openGuestFormModal();
                return;
            }}
            document.getElementById("gasUrlInput").value = apiEndpoint;
            document.getElementById("adminLoginModal").classList.remove("hidden");
            document.getElementById("adminLoginModal").classList.add("flex");
        }}

        function closeAdminModal() {{
            document.getElementById("adminLoginModal").classList.add("hidden");
            document.getElementById("adminLoginModal").classList.remove("flex");
        }}

        async function handleAdminLogin(e) {{
            e.preventDefault();
            const pin = document.getElementById("pinInput").value.trim();
            const urlVal = document.getElementById("gasUrlInput").value.trim();

            if (urlVal) {{
                apiEndpoint = urlVal;
                localStorage.setItem("MAN2_GAS_API_URL", apiEndpoint);
            }}

            if (apiEndpoint) {{
                try {{
                    const res = await fetch(`${{apiEndpoint}}?action=VERIFY_PIN&pin=${{encodeURIComponent(pin)}}`);
                    const json = await res.json();
                    if (!json.valid) {{
                        alert("PIN Petugas tidak sesuai dengan Google Sheet Pengaturan!");
                        return;
                    }}
                }} catch (err) {{
                    console.warn("Verifikasi offline fallback digunakan:", err);
                }}
            }} else if (pin !== "man2kudus" && pin !== "123456") {{
                alert("PIN Demo salah! Gunakan: man2kudus");
                return;
            }}

            adminPin = pin;
            isAdminMode = true;
            sessionStorage.setItem("MAN2_ADMIN_PIN", adminPin);
            updateAdminUiState();
            closeAdminModal();
            if (apiEndpoint) refreshFromServer();
        }}

        function logoutAdmin() {{
            adminPin = "";
            isAdminMode = false;
            sessionStorage.removeItem("MAN2_ADMIN_PIN");
            updateAdminUiState();
        }}

        function updateAdminUiState() {{
            const toolbar = document.getElementById("adminToolbar");
            const btnLabel = document.getElementById("adminBtnLabel");
            if (isAdminMode) {{
                toolbar.classList.remove("hidden");
                btnLabel.textContent = "+ Input Tamu";
            }} else {{
                toolbar.classList.add("hidden");
                btnLabel.textContent = "Petugas FO / Humas";
            }}
            renderGuestCards();
        }}

        // Modal Tambah / Edit Tamu
        function openGuestFormModal(guestObj = null) {{
            document.getElementById("formModalTitle").textContent = guestObj ? "Edit / Update Kelengkapan Tamu" : "Input Data Tamu Baru";
            document.getElementById("fIdTamu").value = guestObj ? guestObj.id_tamu : "";
            document.getElementById("fTanggal").value = guestObj ? guestObj.tanggal : getOffsetDateStr(0);
            document.getElementById("fWaktuMulai").value = guestObj ? guestObj.waktu_mulai : "08:30";
            document.getElementById("fWaktuSelesai").value = guestObj ? guestObj.waktu_selesai : "10:30";
            document.getElementById("fNamaTamu").value = guestObj ? guestObj.nama_tamu : "";
            document.getElementById("fInstansi").value = guestObj ? guestObj.instansi : "";
            document.getElementById("fJumlahOrang").value = guestObj ? guestObj.jumlah_orang : 2;
            document.getElementById("fLokasi").value = guestObj ? guestObj.lokasi : "";
            document.getElementById("fPic").value = guestObj ? guestObj.pic_penyambut : "";
            document.getElementById("fKepentingan").value = guestObj ? guestObj.kepentingan : "";
            document.getElementById("fKegiatan").value = guestObj ? guestObj.kegiatan : "";
            document.getElementById("fStatus").value = guestObj ? guestObj.status : "Akan Hadir";
            document.getElementById("fPetugas").value = guestObj ? guestObj.petugas_input : "Petugas Front Office";

            document.getElementById("guestFormModal").classList.remove("hidden");
            document.getElementById("guestFormModal").classList.add("flex");
        }}

        function closeGuestFormModal() {{
            document.getElementById("guestFormModal").classList.add("hidden");
            document.getElementById("guestFormModal").classList.remove("flex");
        }}

        function editGuest(idTamu) {{
            const g = (appState.guests || []).find(x => x.id_tamu === idTamu);
            if (g) openGuestFormModal(g);
        }}

        async function handleSaveGuest(e) {{
            e.preventDefault();
            const existingId = document.getElementById("fIdTamu").value.trim();
            const newGuest = {{
                id_tamu: existingId || ("TM-" + Date.now()),
                tanggal: document.getElementById("fTanggal").value,
                waktu_mulai: document.getElementById("fWaktuMulai").value,
                waktu_selesai: document.getElementById("fWaktuSelesai").value,
                nama_tamu: document.getElementById("fNamaTamu").value.trim(),
                instansi: document.getElementById("fInstansi").value.trim(),
                jumlah_orang: Number(document.getElementById("fJumlahOrang").value) || 1,
                lokasi: document.getElementById("fLokasi").value.trim(),
                pic_penyambut: document.getElementById("fPic").value.trim(),
                kepentingan: document.getElementById("fKepentingan").value.trim(),
                kegiatan: document.getElementById("fKegiatan").value.trim(),
                status: document.getElementById("fStatus").value,
                petugas_input: document.getElementById("fPetugas").value.trim()
            }};

            // Update lokal instan (Optimistic UI)
            const idx = appState.guests.findIndex(x => x.id_tamu === newGuest.id_tamu);
            if (idx >= 0) {{
                appState.guests[idx] = newGuest;
            }} else {{
                appState.guests.push(newGuest);
            }}
            saveStateToLocal();
            renderGuestCards();
            closeGuestFormModal();

            // Jika API Google Sheet terhubung, kirim ke Cloud
            if (apiEndpoint) {{
                try {{
                    const res = await fetch(apiEndpoint, {{
                        method: "POST",
                        body: JSON.stringify({{ action: "SAVE_GUEST", pin: adminPin, guest: newGuest }})
                    }});
                    const json = await res.json();
                    if (json.status === "success" && json.data) {{
                        appState = json.data;
                        saveStateToLocal();
                        renderGuestCards();
                    }}
                }} catch (err) {{
                    console.warn("Disimpan di memori lokal, sinkronisasi cloud tertunda:", err);
                }}
            }}
        }}

        async function quickStatus(idTamu, newStatus) {{
            const g = appState.guests.find(x => x.id_tamu === idTamu);
            if (!g) return;
            g.status = newStatus;
            saveStateToLocal();
            renderGuestCards();

            if (apiEndpoint) {{
                try {{
                    await fetch(apiEndpoint, {{
                        method: "POST",
                        body: JSON.stringify({{ action: "QUICK_STATUS", pin: adminPin, id_tamu: idTamu, new_status: newStatus }})
                    }});
                }} catch (err) {{}}
            }}
        }}

        async function deleteGuest(idTamu) {{
            if (!confirm("Hapus jadwal tamu ini dari daftar?")) return;
            appState.guests = appState.guests.filter(x => x.id_tamu !== idTamu);
            saveStateToLocal();
            renderGuestCards();

            if (apiEndpoint) {{
                try {{
                    await fetch(apiEndpoint, {{
                        method: "POST",
                        body: JSON.stringify({{ action: "DELETE_GUEST", pin: adminPin, id_tamu: idTamu }})
                    }});
                }} catch (err) {{}}
            }}
        }}

        async function openRunningTextModal() {{
            const currentTxt = document.getElementById("runningTextDisplay").textContent.trim();
            const updated = prompt("Masukkan teks berjalan (Running Text) untuk layar TV Front Office MAN 2 Kudus:", currentTxt);
            if (updated && updated.trim()) {{
                appState.config.RUNNING_TEXT = updated.trim();
                document.getElementById("runningTextDisplay").textContent = updated.trim();
                saveStateToLocal();
                if (apiEndpoint) {{
                    try {{
                        await fetch(apiEndpoint, {{
                            method: "POST",
                            body: JSON.stringify({{ action: "UPDATE_RUNNING_TEXT", pin: adminPin, running_text: updated.trim() }})
                        }});
                    }} catch (err) {{}}
                }}
            }}
        }}

        async function refreshFromServer() {{
            if (!apiEndpoint) {{
                renderGuestCards();
                return;
            }}
            const badge = document.getElementById("syncBadge");
            badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span> Menyinkronkan...`;
            try {{
                const res = await fetch(apiEndpoint);
                const json = await res.json();
                if (json.status === "success" && json.data) {{
                    appState = json.data;
                    saveStateToLocal();
                    populateDropdownLists();
                    renderGuestCards();
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Terhubung ke Sheet`;
                }}
            }} catch (err) {{
                badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-400"></span> Mode Offline Cache`;
            }}
        }}

        window.addEventListener("DOMContentLoaded", () => {{
            updateLiveClock();
            setInterval(updateLiveClock, 1000);
            populateDropdownLists();
            updateAdminUiState();
            setDateFilter("TODAY");
            if (apiEndpoint) refreshFromServer();
            // Auto-refresh setiap 60 detik untuk TV Front Office
            setInterval(() => {{
                if (apiEndpoint) refreshFromServer();
            }}, 60000);
        }});
    </script>
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    build_manifest()
    build_index_html()
    print(f"Successfully generated 'Siapa Tamu Hari Ini! - MAN 2 Kudus' web app in /{OUTPUT_DIR}!")

if __name__ == "__main__":
    main()
