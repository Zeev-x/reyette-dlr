# Work on Windows only
# Created by Reyette
# Thanks for yt-dlp and ffmpeg

import os
import subprocess
import yt_dlp
import threading
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

BASE_DIR = "D:\\Reyette-Downloader"

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|#]', '', name)
    return name.strip().replace(' ', '_')

def detect_encoder():
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW
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

    cmd = ["ffmpeg", "-y", "-i", video_file,"-i", audio_file, "-pix_fmt", "yuv420p", "-c:v", encoder]

    if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
        cmd += [
            "-preset", "slow",
            "-rc:v", "vbr",
            "-cq", "8",
            "-b:v", "16M",
            "-maxrate", "20M",
            "-bufsize", "25M",
        ]
    else:
        cmd += [
            "-preset", "slow",
            "-crf", "23",
        ]

    cmd += ["-c:a", "aac", "-b:a", "320k", output_file]
    return cmd

def single_cmd(video_file, output_file, encoder=None):
    if encoder is None:
        encoder = detect_encoder()

    cmd = ["ffmpeg", "-y", "-i", video_file, "-pix_fmt", "yuv420p", "-c:v", encoder]

    if encoder in ["h264_nvenc", "h264_amf", "h264_qsv"]:
        cmd += [
            "-preset", "slow",
            "-rc:v", "vbr",
            "-cq", "8",
            "-b:v", "16M",
            "-maxrate", "20M",
            "-bufsize", "25M",
        ]
    else:
        cmd += [
            "-preset", "slow",
            "-crf", "23",
        ]

    cmd += ["-c:a", "aac", "-b:a", "320k", output_file]
    return cmd

class DummyLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class DownloaderLayout(BoxLayout):
    def add_log(self, text):
        def update(dt):
            current = self.ids.log.text or ""
            self.ids.log.text = current + str(text) + "\n"
        Clock.schedule_once(update)

    def clear_log(self):
        def update(dt):
            self.ids.log.text = ""
        Clock.schedule_once(update)

    def run_ffmpeg_with_log(self, cmd, output_file):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.add_log(line)
            process.wait()
            if process.returncode == 0:
                self.add_log(f"Encode selesai: {output_file}")
            else:
                self.add_log(f"FFmpeg gagal dengan kode {process.returncode}")
        except Exception as e:
            self.add_log(f"Error ffmpeg: {e}")

    def detect_platform(self, url: str) -> str:
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
        
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            s = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', 'N/A')
            spd = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            self.add_log(f"Downloading {p} of {s} at speed {spd} estimated time {eta}")
        elif d['status'] == 'finished':
            self.add_log("Download selesai")

    def start_download(self):
        url = self.ids.url.text.strip()
        mode = self.ids.mode.text.strip()
        quality = self.ids.quality.text.strip()

        if not url:
            self.add_log("URL kosong!")
            return

        # clear log sebelum mulai download baru
        self.clear_log()

        self.add_log("Menjalankan proses download...")
        threading.Thread(target=self._do_download, args=(url, mode, quality), daemon=True).start()

    def _do_download(self, url, mode, quality):
        platform = self.detect_platform(url)
        self.add_log(f"Mulai mengunduh dari {platform}: {url}")

        if mode == "MP3":
            target_dir = os.path.join(BASE_DIR, "audio", platform)
        else:
            target_dir = os.path.join(BASE_DIR, "video", platform)
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
                'logger': DummyLogger(),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }
        else:
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

            ydl_opts_v = {
                'outtmpl': f'{target_dir}/v_temp.%(ext)s',
                'format': fmt,
                'logger': DummyLogger(),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }

            ydl_opts_a = {
                'outtmpl': f'{target_dir}/a_temp.%(ext)s',
                'format': "bestaudio/best",
                'logger': DummyLogger(),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self.progress_hook],
                'ignoreerrors': True,
            }

        try:
            if platform == "youtube":
                if mode == "MP4":
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
                        cmd = double_cmd(video_file, audio_file, output_file)
                        self.run_ffmpeg_with_log(cmd, output_file)
                        if os.path.exists(video_file):
                            os.remove(video_file)
                        if os.path.exists(audio_file):
                            os.remove(audio_file)
                    else:
                        self.add_log("Error: file hasil download tidak ditemukan!")
                else:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        result_a = ydl.extract_info(url, download=True)
                        audio_file = ydl.prepare_filename(result_a)
                        self.add_log("File MP3 siap digunakan!")

            else:
                if quality == "360p":
                    sfmt = "bestvideo[height<=360]+bestaudio/best"
                elif quality == "480p":
                    sfmt = "bestvideo[height<=480]+bestaudio/best"
                elif quality == "720p":
                    sfmt = "bestvideo[height<=720]+bestaudio/best"
                elif quality == "1080p":
                    sfmt = "bestvideo[height<=1080]+bestaudio/best"
                else:
                    sfmt = "bestvideo+bestaudio/best"

                ydl_opts_sv = {
                    'outtmpl': f'{target_dir}/s_temp.%(ext)s',
                    'format': sfmt,
                    'logger': DummyLogger(),
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self.progress_hook],
                    'ignoreerrors': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts_sv) as ydl:
                    result_s = ydl.extract_info(url, download=True)
                    single_file = ydl.prepare_filename(result_s)
                    if mode == "MP4":
                        base = result_s.get('title') or result_s.get('id') or "video"
                        xname = sanitize_filename(base)[:50]
                        output_file = os.path.join(target_dir, f"{xname}_{quality}.mp4")
                        if os.path.exists(single_file):
                            cmd = single_cmd(single_file, output_file)
                            self.run_ffmpeg_with_log(cmd, output_file)
                            if os.path.exists(single_file):
                                os.remove(single_file)

        except Exception as e:
            self.add_log(f"Error download :{e}")

class DownloaderApp(App):
    def build(self):
        return DownloaderLayout()

if __name__ == "__main__":
    app = DownloaderApp()
    app.icon = os.path.join("icon", "icon.ico")
    app.run()
