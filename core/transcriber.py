
import os
import requests
import whisper

from dotenv import load_dotenv
from pydub import AudioSegment


# Load environment variables before accessing API keys
load_dotenv()

# ---------------- CONFIGURATION ----------------

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"

SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v4")

# Sarvam REST API accepts audio up to 30 seconds
SARVAM_PIECE_SECONDS = 25

_model = None


# ---------------- WHISPER MODEL ----------------

def load_model():

    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")

        _model = whisper.load_model(WHISPER_MODEL)

        print("Whisper model loaded successfully.")

    return _model


# ---------------- WHISPER TRANSCRIPTION ----------------

def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=False,
        verbose=False,
        beam_size=1,
        condition_on_previous_text=False
    )

    return result["text"].strip()


# ---------------- SARVAM API REQUEST ----------------

def _send_to_sarvam(piece_path: str) -> str:

    api_key = os.getenv("SARVAM_API_KEY")

    if not api_key:
        raise RuntimeError(
            "SARVAM_API_KEY is missing. Check your .env file."
        )

    headers = {
        "api-subscription-key": api_key
    }

    data = {
        "model": SARVAM_MODEL,
        "mode": "translate"
    }

    with open(piece_path, "rb") as audio_file:

        files = {
            "file": (
                os.path.basename(piece_path),
                audio_file,
                "audio/wav"
            )
        }

        response = requests.post(
            SARVAM_STT_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=120
        )

    if not response.ok:

        print("\nSarvam API Error:", response.status_code)
        print("Error Details:", response.text)

        response.raise_for_status()

    result = response.json()

    return result.get("transcript", "")


# ---------------- SARVAM TRANSCRIPTION ----------------

def transcribe_chunk_sarvam(chunk_path: str) -> str:

    if not os.getenv("SARVAM_API_KEY"):
        raise RuntimeError(
            "SARVAM_API_KEY is not set in your .env file."
        )

    audio = AudioSegment.from_file(chunk_path)

    # Convert audio into API-friendly WAV format
    audio = (
        audio
        .set_channels(1)
        .set_frame_rate(16000)
        .set_sample_width(2)
    )

    piece_ms = SARVAM_PIECE_SECONDS * 1000

    full_text = ""

    total_pieces = (
        len(audio) + piece_ms - 1
    ) // piece_ms

    for i, start in enumerate(
        range(0, len(audio), piece_ms)
    ):

        piece = audio[start:start + piece_ms]

        piece_path = f"{chunk_path}_sv_{i}.wav"

        piece.export(piece_path, format="wav")

        try:

            print(
                f"  Transcribing Sarvam piece "
                f"{i + 1}/{total_pieces}..."
            )

            text = _send_to_sarvam(piece_path)

            full_text += text + " "

        finally:

            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


# ---------------- TRANSCRIPTION ROUTER ----------------

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    if language.lower() == "hinglish":

        return transcribe_chunk_sarvam(chunk_path)

    return transcribe_chunk_whisper(chunk_path)


# ---------------- TRANSCRIBE ALL CHUNKS ----------------

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = ""

    engine = (
        "Sarvam AI"
        if language.lower() == "hinglish"
        else "Whisper"
    )

    print(f"\nUsing {engine} for transcription.\n")

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk {i + 1}/{len(chunks)}..."
        )

        text = transcribe_chunk(
            chunk,
            language=language
        )

        full_transcript += text + " "

    print("\nTranscription complete.")

    return full_transcript.strip()
