# Created by Reyette
# Thanks for yt-dlp and ffmpeg

import os
import subprocess
import yt_dlp
import re

BASE_DIR = "Reyette-Downloader"

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

def main():
    url = input("Masukkan URL: ").strip()
    mode = input("Pilih mode (MP3/MP4): ").strip().upper()
    quality = input("Pilih kualitas (360p/480p/720p/1080p/max): ").strip().lower()

    platform = detect_platform(url)
    print(f"Mulai mengunduh dari {platform}: {url}")

    target_dir = os.path.join(BASE_DIR, "audio" if mode == "MP3" else "video", platform)
    os.makedirs(target_dir, exist_ok=True)

    if mode == "MP3":
        ydl_opts = {
            'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(result)
        print(f"✅ File MP3 siap: {audio_file}")

    else:  # MP4
        if quality == "360p":
            fmt = "bestvideo[height<=360]"
        elif quality == "480p":
            fmt = "bestvideo[height<=480]"
        elif quality == "720p":
            fmt = "bestvideo[height<=720]"
        elif quality == "1080p":
            fmt = "bestvideo[height<=1080]"
        else:
            fmt = "bestvideo"

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
    main()
