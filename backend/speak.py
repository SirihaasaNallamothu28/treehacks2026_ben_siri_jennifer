import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("HEYGEN_API_KEY")


def send_script(session_data, text):
    url = "https://api.heygen.com/v1/streaming.task"

    headers = {
        "Authorization": f"Bearer {session_data['access_token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "session_id": session_data['session_id'],
        "text": text
    }

    resp = requests.post(url, json=payload, headers=headers)
    print(f"Sent script task: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error sending script: {resp.text}")
