import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://api.heygen.com/v2"
OUTPUT_DIR = "heygen_videos"


def _replace_placeholders(obj, replacements):
    if isinstance(obj, dict):
        return {k: _replace_placeholders(v, replacements) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_placeholders(i, replacements) for i in obj]
    elif isinstance(obj, str):
        for key, val in replacements.items():
            obj = obj.replace("{{" + key + "}}", str(val))
        return obj
    return obj


def generate_from_perplexity_json(
    json_str: str,
    output_path: str,
    avatar_id: str = "",
    voice_id: str = "",
    width: int = 1080,
    height: int = 1920,
):
    """
    Parse strict JSON string (e.g. from Perplexity) and generate HeyGen video via v1 API.
    """
    body = json.loads(json_str)
    reps = {}
    if avatar_id:
        reps["AVATAR_ID"] = avatar_id
    if voice_id:
        reps["VOICE_ID"] = voice_id
    if width:
        reps["WIDTH"] = width
    if height:
        reps["HEIGHT"] = height
    if reps:
        body = _replace_placeholders(body, reps)
    if width and height:
        body["dimension"] = {"width": int(width), "height": int(height)}
    return generate_heygen_video_v2_from_body(body=body, output_path=output_path)


def generate_heygen_video_v2_from_body(
    body: dict,
    output_path: str,
    poll_interval: int = 5,
):
    """
    Sends a pre-built body to HeyGen v1 video.generate,
    polls until completion, then downloads the video.

    Parameters:
        body (dict): Fully constructed request body
        output_path (str): Where to save the downloaded video
        poll_interval (int): Seconds between status checks
    """

    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        raise ValueError("HEYGEN_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    # 🔹 1️⃣ Start Video
    response = requests.post(
        f"{BASE_URL}/video/generate",
        headers=headers,
        json=body
    )
    
    # Print error details if request fails
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
    
    response.raise_for_status()

    resp_json = response.json()
    video_id = resp_json.get("data", {}).get("video_id")

    if not video_id:
        raise RuntimeError(f"Failed to start video generation: {resp_json}")

    print("🎬 Video started:", video_id)

    # 🔹 2️⃣ Poll Status (v1 returns status at top level, result.download_url when done)
    download_url = None
    while True:
        status_response = requests.get(
            f"{BASE_URL}/video/status/{video_id}",
            headers=headers
        )
        status_response.raise_for_status()
        status_json = status_response.json()

        status = status_json.get("status")
        print("⏳ Status:", status)

        if status == "completed":
            download_url = status_json.get("result", {}).get("download_url")
            if download_url:
                break
        elif status == "failed":
            raise RuntimeError("Video generation failed")

        time.sleep(poll_interval)

    if not download_url:
        raise RuntimeError(f"No download URL found: {status_json}")

    # 🔹 3️⃣ Download and save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    full_path = os.path.join(OUTPUT_DIR, os.path.basename(output_path))
    print("⬇ Downloading video to", full_path)
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(full_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("Saved to:", full_path)
    return full_path
