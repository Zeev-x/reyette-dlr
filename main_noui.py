# Created by Reyette
# Thanks for yt-dlp and ffmpeg

import os
import subprocess
import yt_dlp
import re
import requests

BASE_DIR = "Reyette-Downloader"
COVER_URL = "https://raw.githubusercontent.com/Zeev-x/jalanin-dulu/refs/heads/main/HOEizhAacAAU07P.jpg"

def get_url():
    while True:
        x_url = input("Masukkan URL: ").strip()
        if x_url == "":
            print("Masukan Valid URL!")
        else:
            return x_url

def get_type():
    while True:
        x_type = input("Pilih mode (MP3/MP4): ").strip().upper()
        if x_type == "MP3":
            return x_type
        elif x_type == "MP4":
            return x_type
        else:
            print("Pilih mode yang sesuai! (mp3/mp4)")

def get_quality():
    while True:
            x_qual = input("Pilih kualitas (360p/480p/720p/1080p/max): ").strip().lower()
            if x_qual == "360p" or x_qual == "360":
                return "bestvideo[height<=360]"
            elif x_qual == "480p" or x_qual == "480":
                return "bestvideo[height<=480]"
            elif x_qual == "720p" or x_qual == "720":
                return "bestvideo[height<=720]"
            elif x_qual == "1080p" or x_qual == "1080":
                return "bestvideo[height<=1080]"
            elif x_qual == "max":
                return "bestvideo"
            else:
                print("Pilih kualitas yang valid!")

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|#]', '', name)
    return name.strip().replace(' ', '_')

def detect_encoder():
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
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

def double_cmd(video_file, audio_file, output_file, encoder=None):
    if encoder is None:
        encoder = detect_encoder()
    cmd = ["ffmpeg", "-y", "-i", video_file, "-i", audio_file,
           "-pix_fmt", "yuv420p", "-c:v", encoder]
    if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
        cmd += ["-preset", "slow", "-rc:v", "vbr", "-cq", "8",
                "-b:v", "16M", "-maxrate", "20M", "-bufsize", "25M"]
    else:
        cmd += ["-preset", "slow", "-crf", "23"]
    cmd += ["-c:a", "aac", "-b:a", "320k", output_file]
    return cmd

def single_cmd(video_file, output_file, encoder=None):
    if encoder is None:
        encoder = detect_encoder()
    cmd = ["ffmpeg", "-y", "-i", video_file,
           "-pix_fmt", "yuv420p", "-c:v", encoder]
    if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
        cmd += ["-preset", "slow", "-rc:v", "vbr", "-cq", "8",
                "-b:v", "16M", "-maxrate", "20M", "-bufsize", "25M"]
    else:
        cmd += ["-preset", "slow", "-crf", "23"]
    cmd += ["-c:a", "aac", "-b:a", "320k", output_file]
    return cmd

def audio_cmd(audio_file, output_file, cover_url, encoder="aac"):
    cover_file = os.path.join(
        os.path.dirname(output_file),
        os.path.splitext(os.path.basename(audio_file))[0] + "_cover.jpg"
    )

    try:
        r = requests.get(cover_url, timeout=10)
        r.raise_for_status()
        with open(cover_file, "wb") as f:
            f.write(r.content)
    except Exception as e:
        print(f"[ERROR] Gagal download cover: {e}")
        return None

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_file,
        "-i", cover_file,
        "-map", "0:a", "-map", "1:v",
        "-c:a", "libmp3lame", "-q:a", "0",
        "-c:v", "mjpeg",
        "-disposition:v", "attached_pic",
        "-id3v2_version", "3",
        "-metadata:s:v", "title=Reyette Atelier",
        "-metadata:s:v", "comment=Premium Downloader",
        output_file
    ]

    process = subprocess.run(cmd)

    # cleanup cover
    if process.returncode == 0 and os.path.exists(cover_file):
        os.remove(cover_file)

    if process.returncode == 0 and os.path.exists(audio_file):
        os.remove(audio_file)

    return cmd

def detect_platform(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    elif "instagram.com" in url:
        return "instagram"
    elif "xhamster.com" in url:
        return "xhamster"
    elif "xvideos.com" in url:
        return "xvideos"
    elif "xnxx.com" in url:
        return "xnxx"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    else:
        return "other"

def do_work():
    url = get_url()
    mode = get_type()

    platform = detect_platform(url)
    print(f"Mulai mengunduh dari {platform}: {url}")

    target_dir = os.path.join(BASE_DIR, "audio" if mode == "MP3" else "video", platform)
    os.makedirs(target_dir, exist_ok=True)

    if mode == "MP3":
        ydl_opts = {
            'outtmpl': f'{target_dir}/a_temp.%(ext)s',
            'format': 'bestaudio/best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(result)

        base = result.get('title') or result.get('id') or "audio"
        xname = sanitize_filename(base)
        output_file = os.path.join(target_dir, f"{xname}.mp3")

        if audio_cmd(audio_file, output_file, COVER_URL):
            print(f"✅ File MP3 siap: {output_file}")
        else:
             print("❌ Gagal encode audio")

    else:  # MP4
        fmt = get_quality()

        ydl_opts_v = {'outtmpl': f'{target_dir}/v_temp.%(ext)s', 'format': fmt}
        ydl_opts_a = {'outtmpl': f'{target_dir}/a_temp.%(ext)s', 'format': 'bestaudio/best'}

        with yt_dlp.YoutubeDL(ydl_opts_v) as ydl:
            result_v = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(result_v)

        with yt_dlp.YoutubeDL(ydl_opts_a) as ydl:
            result_a = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(result_a)

        base = result_v.get('title') or result_v.get('id') or "video"
        xname = sanitize_filename(base)
        output_file = os.path.join(target_dir, f"{xname}_{quality}.mp4")

        if os.path.exists(video_file) and os.path.exists(audio_file):
            print("🔄 Mulai proses encode...")
            cmd = double_cmd(video_file, audio_file, output_file)
            subprocess.run(cmd, check=True)
            print(f"✅ Encode selesai: {output_file}")
            os.remove(video_file)
            os.remove(audio_file)
        else:
            print("❌ Error: file hasil download tidak ditemukan!")

if __name__ == "__main__":
    do_work()
