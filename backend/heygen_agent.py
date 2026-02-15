# heygen_video_agent.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
import time
import requests

BASE_URL = "https://api.heygen.com"

def generate_video_agent(
    prompt: str,
    title: str,
    output_path: str,
):
    """
    Generates a video using HeyGen Video Agent (one-shot prompt → video).
    """

    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        raise ValueError("HEYGEN_API_KEY must be set")
    api_key = api_key.strip()

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    body = {
        "prompt": prompt
    }

    # 1) Start generation
    response = requests.post(
        f"{BASE_URL}/v1/video_agent/generate",
        headers=headers,
        json=body,
        timeout=60,
    )

    try:
        resp_json = response.json()
    except ValueError:
        resp_json = {"status_code": response.status_code, "raw_text": response.text[:500]}

    if response.status_code in (401, 403):
        raise RuntimeError(
            "HeyGen auth failed for /v1/video_agent/generate. "
            "Your API key is invalid/revoked, from the wrong HeyGen workspace, "
            "or your plan does not include Video Agent access. "
            f"status={response.status_code}, response={resp_json}"
        )

    video_id = (resp_json.get("data") or {}).get("video_id")

    if not video_id:
        raise RuntimeError(f"Agent generation failed: {resp_json}")

    print("Video started:", video_id)

    # 2) Poll status
    status_url = f"{BASE_URL}/v1/video_status.get?video_id={video_id}"

    while True:
        status_resp = requests.get(status_url, headers=headers).json()
        status = status_resp.get("data", {}).get("status")

        print("Status:", status)

        if status == "completed":
            download_url = status_resp["data"]["video_url"]
            break
        elif status == "failed":
            raise RuntimeError("Video generation failed")

        time.sleep(5)

    # 3) Download video locally
    print("Downloading video...")
    dl_resp = requests.get(download_url, stream=True)
    dl_resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in dl_resp.iter_content(8192):
            f.write(chunk)

    print("Saved to:", output_path)
    return output_path





# # heygen_agent.py

# import os
# import time
# import requests
# from dotenv import load_dotenv

# load_dotenv()

# BASE_URL = "https://api.heygen.com/v2"


# def generate_ai_agent_video(
#     prompt: str,
#     max_seconds: int,
#     avatar_id: str,
#     voice_id: str,
#     title: str,
#     output_path: str,
#     on_screen_instruction: str = "",
# ):
#     """
#     Uses HeyGen AI-style prompting to generate a video.
#     Caps spoken content to ~30 seconds.
#     """

#     api_key = os.getenv("HEYGEN_API_KEY")
#     if not api_key:
#         raise ValueError("HEYGEN_API_KEY not set")

#     if max_seconds > 30:
#         max_seconds = 30  # hard cap

#     # Estimate 2.5 words per second → ~75 words for 30 sec
#     max_words = int(max_seconds * 2.5)

#     enhanced_prompt = f"""
#     Create a professional academic explainer video script.
#     Keep it under {max_seconds} seconds of speaking.
#     Limit to approximately {max_words} words maximum.
#     Tone: clear, confident, research-oriented.

#     On-screen display guidance:
#     {on_screen_instruction}

#     Topic:
#     {prompt}
#     """

#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "X-Api-Key": api_key
#     }

#     body = {
#         "caption": False,
#         "title": title,
#         "video_inputs": [
#             {
#                 "character": {
#                     "type": "avatar",
#                     "avatar_id": avatar_id
#                 },
#                 "voice": {
#                     "type": "text",
#                     "voice_id": voice_id,
#                     "input_text": enhanced_prompt,
#                     "speed": 1.05
#                 },
#                 "background": {
#                     "type": "color",
#                     "value": "#F4F4F4"
#                 }
#             }
#         ],
#         "dimension": {
#             "width": 1080,
#             "height": 1920
#         }
#     }

#     # 1️⃣ Generate
#     response = requests.post(
#         f"{BASE_URL}/video/generate",
#         headers=headers,
#         json=body
#     )

#     resp_json = response.json()
#     video_id = (resp_json.get("data") or {}).get("video_id")

#     if not video_id:
#         raise RuntimeError(f"Generation failed: {resp_json}")

#     print("Video started:", video_id)

#     # 2️⃣ Poll status (use v1 endpoint - v2 status returns non-JSON)
#     status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

#     while True:
#         r = requests.get(status_url, headers=headers)
#         try:
#             status_resp = r.json() if r.content else {}
#         except Exception:
#             raise RuntimeError(f"Status endpoint returned non-JSON (status {r.status_code}): {r.text[:200]}")
#         status = status_resp.get("status")

#         print("Status:", status)

#         if status == "completed":
#             download_url = status_resp["result"]["download_url"]
#             break
#         elif status == "failed":
#             raise RuntimeError("Video generation failed")

#         time.sleep(5)

#     # 3️⃣ Download locally
#     print("Downloading...")
#     r = requests.get(download_url, stream=True)
#     r.raise_for_status()

#     with open(output_path, "wb") as f:
#         for chunk in r.iter_content(8192):
#             f.write(chunk)

#     print("Saved to:", output_path)
#     return output_path
