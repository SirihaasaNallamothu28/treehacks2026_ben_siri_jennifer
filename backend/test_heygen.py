"""
Quick test to verify HeyGen API is working
"""
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

api_key = os.getenv("HEYGEN_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "NO API KEY")

headers = {
    "Content-Type": "application/json",
    "X-Api-Key": api_key
}

# Test with a simple prompt
body = {
    "prompt": "Create a 10 second video explaining what machine learning is in simple terms."
}

print("\n🔄 Calling HeyGen Video Agent API...")
print(f"Endpoint: https://api.heygen.com/v1/video_agent/generate")

response = requests.post(
    "https://api.heygen.com/v1/video_agent/generate",
    headers=headers,
    json=body,
    timeout=60,
)

print(f"\n📊 Response Status: {response.status_code}")
print(f"📝 Response Headers: {dict(response.headers)}")

try:
    resp_json = response.json()
    print(f"\n✅ Response JSON:")
    import json
    print(json.dumps(resp_json, indent=2))
except Exception as e:
    print(f"\n❌ Could not parse JSON: {e}")
    print(f"Raw response: {response.text[:500]}")
