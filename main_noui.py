# Work on Windows, linux, an Android.
# Created by Reyette.
# Thanks for yt-dlp and ffmpeg.
# Not recomended runing on android, because it will take a long time to encode video using CPU (libx264).

import os
import subprocess
import yt_dlp

BASE_DIR = "Reyette-Downloader"

def detect_encoder():
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, encoding="utf-8")
        encoders = result.stdout.lower()
        if "h264_nvenc" in encoders:
            return "h264_nvenc"   # NVIDIA
        elif "h264_amf" in encoders:
            return "h264_amf"     # AMD
        elif "h264_qsv" in encoders:
            return "h264_qsv"     # Intel QuickSync
        else:
            return "libx264"      # Fallback CPU
    except Exception:
        return "libx264"

def build_ffmpeg_cmd(input_file, output_file, encoder=None):
    if encoder is None:
        encoder = detect_encoder()

    cmd = ["ffmpeg", "-i", input_file, "-c:v", encoder]

    if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
        # GPU encoder → pakai CQ
        cmd += [
            "-preset", "slow",
            "-rc:v", "vbr",
            "-cq", "8",
            "-b:v", "16M",
            "-maxrate", "20M",
            "-bufsize", "25M",
        ]
    else:
        # CPU libx264 → pakai CRF
        cmd += [
            "-preset", "slow",
            "-crf", "23",   # default CRF untuk kualitas seimbang
        ]

    cmd += ["-c:a", "aac", "-b:a", "320k", output_file]
    return cmd, encoder

def downloaderMain():
    url = input("Masukkan URL: ").strip()
    mode = input("Pilih mode (MP3/MP4): ").strip().upper()
    quality = input("Pilih kualitas (360p/480p/720p/1080p/max): ").strip().lower()

    def detect_platform(url: str) -> str:
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube"
        elif "tiktok.com" in url:
            return "tiktok"
        elif "facebook.com" in url:
            return "facebook"
        elif "instagram.com" in url:
            return "instagram"
        elif "twitter.com" in url or "x.com" in url:
            return "twitter"
        else:
            return "other"
    
    if not url:
        print("URL tidak boleh kosong!")
        return
    
    print("Menjalankan proses download...")

    def _do_download(url, mode, quality):
        platform = detect_platform(url)
        print(f"Mulai mengunduh dari {platform}: {url} ({mode}, {quality}) → {platform}")

        if mode == "MP3":
            target_dir = os.path.join(BASE_DIR, "audio", platform)
        else:
            target_dir = os.path.join(BASE_DIR, "video", platform)
        os.makedirs(target_dir, exist_ok=True)

        # Opsi yt_dlp
        if mode == "MP3":
            ydl_opts = {
                'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
        else:
            if quality == "360p":
                fmt = "bestvideo[height<=360]+bestaudio/best"
            elif quality == "480p":
                fmt = "bestvideo[height<=480]+bestaudio/best"
            elif quality == "720p":
                fmt = "bestvideo[height<=720]+bestaudio/best"
            elif quality == "1080p":
                fmt = "bestvideo[height<=1080]+bestaudio/best"
            else:
                fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                'format': fmt,
                'merge_output_format': 'mp4',
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # Playlist
                    for entry in info['entries']:
                        if not entry:
                            continue
                        try:
                            entry_url = entry.get('url') or entry.get('webpage_url')
                            if not entry_url:
                                print("Entry playlist tidak punya URL, skip.")
                                continue

                            result = ydl.extract_info(entry_url, download=True)
                            input_file = ydl.prepare_filename(result)

                            if mode == "MP4":
                                base, _ = os.path.splitext(input_file)
                                output_file = f"{base}_{quality}.mp4"
                                cmd, encoder = build_ffmpeg_cmd(input_file, output_file)
                                print(f"🔍 Encoder terdeteksi: {encoder}")
                                subprocess.run(cmd, check=True, stderr=subprocess.STDOUT)
                                print(f"Konversi selesai: {output_file}")
                                if os.path.exists(input_file):
                                    os.remove(input_file)
                            else:
                                print("File MP3 siap digunakan!")

                        except Exception as e:
                            print(f"Error item playlist: {e}")
                else:
                    # Single video fallback
                    result = ydl.extract_info(url, download=True)
                    input_file = ydl.prepare_filename(result)
                    print(f"Selesai unduh dan mulai encode")
                    if mode == "MP4":
                        base, _ = os.path.splitext(input_file)
                        output_file = f"{base}_{quality}.mp4"
                        cmd, encoder = build_ffmpeg_cmd(input_file, output_file)
                        print(f"🔍 Encoder terdeteksi: {encoder}")
                        subprocess.run(cmd, check=True, stderr=subprocess.STDOUT)
                        print(f"Encode selesai: {output_file}")
                        if os.path.exists(input_file):
                            os.remove(input_file)

        except Exception as e:
            print(f"Error download :{e}")

    _do_download(url, mode, quality)

if __name__ == "__main__":
    downloaderMain()
