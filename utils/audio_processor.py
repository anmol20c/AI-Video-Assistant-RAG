
import yt_dlp
from pydub import AudioSegment
import os
import glob
import shutil

# ==========================================
# CROSS-PLATFORM FFMPEG CONFIGURATION
# ==========================================

FFMPEG_BIN = shutil.which("ffmpeg")
FFPROBE_PATH = shutil.which("ffprobe")

# Windows fallback: Locate FFmpeg installed through WinGet
if not FFMPEG_BIN and os.name == "nt":
    local_app_data = os.getenv("LOCALAPPDATA", "")
    
    if local_app_data:
        ffmpeg_pattern = os.path.join(
            local_app_data,
            "Microsoft",
            "WinGet",
            "Packages",
            "Gyan.FFmpeg.Shared*",
            "**",
            "bin",
            "ffmpeg.exe"
        )

        ffmpeg_files = glob.glob(
            ffmpeg_pattern, recursive=True
        )

        if ffmpeg_files:
            FFMPEG_BIN = ffmpeg_files[0]
            FFPROBE_PATH = os.path.join(
                os.path.dirname(FFMPEG_BIN),
                "ffprobe.exe"
            )

if not FFMPEG_BIN:
    raise FileNotFoundError(
        "FFmpeg not found. Install FFmpeg or check packages.txt."
    )

if not FFPROBE_PATH:
    raise FileNotFoundError("FFprobe not found.")

# Configure Pydub
AudioSegment.converter = FFMPEG_BIN
AudioSegment.ffmpeg = FFMPEG_BIN
AudioSegment.ffprobe = FFPROBE_PATH

print("FFmpeg configured successfully!")

# ==========================================
# DOWNLOAD DIRECTORY
# ==========================================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ==========================================
# YOUTUBE AUDIO DOWNLOAD
# ==========================================

def download_youtube_audio(url: str) -> str:

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": FFMPEG_BIN,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + ".wav"

    if not os.path.exists(filename):
        raise FileNotFoundError(
            f"Downloaded WAV file not found: {filename}"
        )

    return filename


# ==========================================
# AUDIO CONVERSION
# ==========================================

def convert_to_wav(input_path: str) -> str:

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)

    audio = audio.set_channels(1).set_frame_rate(16000)

    audio.export(output_path, format="wav")

    return output_path


# ==========================================
# AUDIO CHUNKING
# ==========================================

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):

        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

    return chunks


# ==========================================
# MAIN INPUT PROCESSOR
# ==========================================

def process_input(source: str) -> list:

    if source.startswith(("http://", "https://")):

        print("Detected YouTube URL. Downloading audio...")

        wav_path = download_youtube_audio(source)

    else:

        print("Detected local file. Converting to WAV...")

        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks
