
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from utils.audio_processor import process_input
from core.transcriber import transcribe_all


# Check API key
api_key = os.getenv("SARVAM_API_KEY")

if not api_key:
    raise ValueError("SARVAM_API_KEY is missing. Check your .env file.")

print("SARVAM API KEY: Loaded successfully")
print("CWD:", os.getcwd())


# YouTube video URL
source = "https://www.youtube.com/watch?v=Wtmz66dQQxo"

# Select transcription language
language = "hinglish"  # Change to "english" to test Whisper


# Download and process audio
print("\nDownloading and processing audio...")

chunks = process_input(source)

print(f"Audio ready - {len(chunks)} chunk(s) created.")


# Transcribe audio
print("\nStarting transcription...")

transcript = transcribe_all(
    chunks,
    language=language
)


# Display transcript
print("\n=== TRANSCRIPT ===\n")
print(transcript)

print("\nTranscription completed successfully!")
