# Reyette Downloader & Converter 🎬🎵

Reyette adalah tool sederhana berbasis **Python + FFmpeg + yt-dlp** untuk mengunduh video/audio dari berbagai platform (YouTube, TikTok, Instagram, Facebook, Twitter/X) dan mengonversinya ke format MP4/MP3 dengan dukungan **GPU encoder** (NVENC, AMF, QSV) maupun fallback CPU (libx264).

---

## ✨ Fitur Utama
- 🔍 Deteksi otomatis encoder (NVIDIA, AMD, Intel, CPU).
- 🎥 Download video dengan berbagai kualitas.
- 🎵 Ekstrak audio MP3 dengan kualitas 192 kbps.
- ⚡ Konversi cepat menggunakan GPU encoder bila tersedia.
- 📂 Output tersimpan rapi per platform (`audio/` dan `video/`).
- 🛡️ Fallback otomatis ke CPU libx264 jika GPU tidak mendukung.

---

## 📦 Persyaratan
- Gunakan Python 3.12 (jika ingin pakai ui)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/download.html) (pastikan ada di PATH)
- Driver GPU terbaru (jika ingin pakai NVENC/AMF/QSV)

How to use with ui (Work on windows only):
```bash
- pip install -r requirements.txt
- start.bat
```

How to use no ui:
```bash
- pip install yt-dlp
- curl https://zeev-x.github.io/reyette-dlr/main_noui.py >> main_noui.py
- python main_noui.py
```

How to build:
```bash
- curl https://raw.githubusercontent.com/Zeev-x/reyette-dlr/main/builder.py | python
```
## Tahnks to
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* [Reyette](https://github.com/Zeev-x)
