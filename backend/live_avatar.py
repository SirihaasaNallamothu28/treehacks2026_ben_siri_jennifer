import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("HEYGEN_API_KEY")


def create_access_token():
    url = "https://api.heygen.com/v1/streaming.create_token"
    headers = {
        "x-api-key": API_KEY  # Note: HeyGen uses x-api-key for authentication
    }
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["data"]["token"]

def create_session():
    # 1. Get Access Token
    access_token = create_access_token()
    
    # 2. Create Session
    url = "https://api.heygen.com/v1/streaming.new"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "quality": "medium"
        # Using default avatar and voice
    }
    
    print(f"Creating session with token: {access_token[:10]}...")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        raise RuntimeError(f"Failed to create session: {response.text}")
        
    data = response.json().get("data", {})
    # Map 'session_id' correctly if the key differs
    # The Streaming API returns { "data": { "session_id": "...", "sdp": {...}, ... } }
    data["access_token"] = access_token
    return data
