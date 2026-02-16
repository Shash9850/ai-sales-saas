import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

def generate_tts_audio(text: str):

    url = "https://api.sarvam.ai/text-to-speech/stream"

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "target_language_code": "hi-IN",
        "speaker": "shubh",
        "model": "bulbul:v3",
        "pace": 1.0,
        "speech_sample_rate": 22050,
        "output_audio_codec": "mp3",
        "enable_preprocessing": True
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)

    if response.status_code != 200:
        print("TTS ERROR:", response.status_code, response.text)
        return None

    audio_bytes = b""

    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            audio_bytes += chunk

    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

    return audio_base64
