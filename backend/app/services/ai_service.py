import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"


def generate_sales_response(prompt: str):

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sarvam-m",   # we can adjust model later
        "messages": [
            {"role": "system", "content": "You are a persuasive Hindi salesman helping customers choose products."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(SARVAM_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Error from Sarvam API: {response.text}"

    result = response.json()

    return result["choices"][0]["message"]["content"]
