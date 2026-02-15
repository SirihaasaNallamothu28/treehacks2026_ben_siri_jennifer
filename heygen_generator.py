# heygen_generator.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file into environment
import time
import requests


BASE_URL = "https://api.heygen.com/v2"


def generate_heygen_video(
    script_text: str,
    avatar_id: str,
    voice_id: str,
    title: str,
    output_path: str,
):
    """
    Generates a HeyGen video and downloads it locally.
    Returns the saved file path.
    """

    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        raise ValueError("HEYGEN_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    body = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": script_text,
                    "voice_id": voice_id
                }
            }
        ],
        "dimension": {"width": 1080, "height": 1920},

        "title": title
    }


    response = requests.post(
        f"{BASE_URL}/video/generate",
        headers=headers,
        json=body
    )

    resp_json = response.json()
    video_id = (resp_json.get("data") or {}).get("video_id")

    if not video_id:
        raise RuntimeError(f"Failed to start video generation: {resp_json}")

    print("Video started:", video_id)

    
    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

    while True:
        status_resp = requests.get(status_url, headers=headers).json()
        status = status_resp.get("status")

        print("Status:", status)

        if status == "completed":
            download_url = status_resp["result"]["download_url"]
            break
        elif status == "failed":
            raise RuntimeError("Video generation failed")

        time.sleep(5)

    # 3️⃣ Download
    print("Downloading video...")
    for attempt in range(3):
        try:
            r = requests.get(download_url, stream=True, timeout=120)
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"Download failed after 3 attempts: {e}") from e
            print(f"Download attempt {attempt + 1} failed, retrying...")
            time.sleep(2)

    print("Saved to:", output_path)
    return output_path


def _replace_placeholders(obj, replacements):
    """Recursively replace {{KEY}} in strings with replacements['KEY']."""
    if isinstance(obj, dict):
        return {k: _replace_placeholders(v, replacements) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_placeholders(i, replacements) for i in obj]
    elif isinstance(obj, str):
        for key, val in replacements.items():
            obj = obj.replace("{{" + key + "}}", str(val))
        return obj
    return obj


def generate_heygen_video_from_body(
    body: dict,
    output_path: str,
    avatar_id: str = "",
    voice_id: str = "",
    width: int = 1920,
    height: int = 1080,
    replacements: dict = None,
):
    """
    Send a pre-built body to HeyGen v2 video/generate, poll until done, download.
    Supports {{AVATAR_ID}}, {{VOICE_ID}}, {{WIDTH}}, {{HEIGHT}} placeholders.
    Pass avatar_id/voice_id/width/height or use replacements dict.
    """
    reps = replacements or {}
    if avatar_id:
        reps["AVATAR_ID"] = avatar_id
    if voice_id:
        reps["VOICE_ID"] = voice_id
    if width:
        reps["WIDTH"] = width
    if height:
        reps["HEIGHT"] = height
    body = _replace_placeholders(body, reps) if reps else body
    # Ensure dimension uses integers
    if width and height:
        body["dimension"] = {"width": int(width), "height": int(height)}

    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        raise ValueError("HEYGEN_API_KEY environment variable not set")

    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}

    response = requests.post(f"{BASE_URL}/video/generate", headers=headers, json=body)
    resp_json = response.json()
    video_id = (resp_json.get("data") or {}).get("video_id")

    if not video_id:
        raise RuntimeError(f"Failed to start video generation: {resp_json}")

    print("Video started:", video_id)

    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    while True:
        status_resp = requests.get(status_url, headers=headers).json()
        status = status_resp.get("status")
        print("Status:", status)
        if status == "completed":
            download_url = status_resp["result"]["download_url"]
            break
        elif status == "failed":
            raise RuntimeError("Video generation failed")
        time.sleep(5)

    print("Downloading video...")
    for attempt in range(3):
        try:
            r = requests.get(download_url, stream=True, timeout=120)
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"Download failed after 3 attempts: {e}") from e
            print(f"Download attempt {attempt + 1} failed, retrying...")
            time.sleep(2)

    print("Saved to:", output_path)
    return output_path


# # heygen_generator.py

# import os
# import time
# import requests


# BASE_URL = "https://api.heygen.com/v2"


# def generate_heygen_video(
#     script_text: str,
#     avatar_id: str,
#     voice_id: str,
#     title: str,
#     output_path: str,
# ):
#     """
#     Generates a HeyGen video and downloads it locally.
#     Returns the saved file path.
#     """

#     api_key = os.getenv("HEYGEN_API_KEY")
#     if not api_key:
#         raise ValueError("HEYGEN_API_KEY environment variable not set")

#     headers = {
#         "Content-Type": "application/json",
#         "X-Api-Key": api_key
#     }

#     body = {
#         "video_inputs": [
#             {
#                 "character": {
#                     "type": "avatar",
#                     "avatar_id": avatar_id,
#                     "avatar_style": "normal"
#                 },
#                 "voice": {
#                     "type": "text",
#                     "input_text": script_text,
#                     "voice_id": voice_id
#                 }
#             }
#         ],
#         "dimension": {"width": 1080, "height": 1920},
#         "title": title
#     }

#     # 1️⃣ Start generation
#     response = requests.post(
#         f"{BASE_URL}/video/generate",
#         headers=headers,
#         json=body
#     )

#     resp_json = response.json()
#     video_id = (resp_json.get("data") or {}).get("video_id")

#     if not video_id:
#         raise RuntimeError(f"Failed to start video generation: {resp_json}")

#     print("Video started:", video_id)

#     # 2️⃣ Poll status
#     status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

#     while True:
#         status_resp = requests.get(status_url, headers=headers).json()
#         status = status_resp.get("status")

#         print("Status:", status)

#         if status == "completed":
#             download_url = status_resp["result"]["download_url"]
#             break
#         elif status == "failed":
#             raise RuntimeError("Video generation failed")

#         time.sleep(5)

#     # 3️⃣ Download
#     video_data = requests.get(download_url).content

#     with open(output_path, "wb") as f:
#         f.write(video_data)

#     print("Saved to:", output_path)
#     return output_path







# # import os
# # import time
# # import requests

# # # -----------------------
# # # CONFIG
# # # -----------------------
# # API_KEY = os.getenv("HEYGEN_API_KEY")  # Make sure you set this
# # OUTPUT_DIR = "heygen_videos"
# # os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Your script
# script_text = """
# HeyGen-Friendly Video Script  IIH Clinical Research (1 min)

# Scene 1  Opening

# Background: Calm, neutral

# Avatar: Female researcher, relaxed posture, facing camera

# On-Screen Text (0:00-0:05):
# Inflammatory Markers in Idiopathic Intracranial Hypertension (IIH)

# Voiceover / Avatar:
# “Hi, today I want to share findings from a recent study on idiopathic intracranial hypertension, or IIH, a condition where pressure inside the skull rises without a clear cause.”

# Visual Cue: Avatar speaking directly to camera

# Scene 2 IIH Diagram

# Background: Simple diagram of head showing fluid pressure inside skull

# On-Screen Text (0:06-0:12):
# IIH = Increased pressure inside the skull without known cause

# Voiceover / Avatar:
# “In IIH, this increased pressure can affect vision and cause headaches. Researchers wanted to see if inflammation in the body plays a role.”

# Visual Cue: Overlay diagram with fluid pressure illustration

# Scene 3 Eye Diagram

# Background: Eye diagram highlighting retinal layers

# On-Screen Text (0:13-0:18):
# RNFL = Retinal Nerve Fiber Layer the part of the eye that sends visual signals to the brain

# Voiceover / Avatar:
# “They looked at the retinal nerve fiber layer, or RNFL, which is crucial for sending visual information to the brain, to see if it relates to inflammation.”

# Visual Cue: Highlight RNFL layer in diagram

# Scene 4 Blood Cells

# Background: Animated blood cells moving through a vein

# On-Screen Text (0:19-0:25):
# Markers measured: Neutrophils, Platelets, Immature Granulocytes

# Voiceover / Avatar:
# “Blood tests measured different inflammatory cells, including neutrophils, platelets, and immature granulocytes, along with combined markers called SII and SIRI.”

# Visual Cue: Show animated blood cells

# Scene 5 Bar Graph

# Background: Bar graph comparing healthy controls vs IIH patients

# On-Screen Text (0:26-0:30):
# Finding: Patients with IIH had higher inflammatory markers

# Voiceover / Avatar:
# “The study found these markers were higher in people with IIH compared to healthy individuals.”

# Visual Cue: Highlight differences in bars

# Scene 6 RNFL Thickness

# Background: Eye diagram with RNFL thickness highlighted

# On-Screen Text (0:31-0:36):
# Thicker RNFL correlated with higher inflammation

# Voiceover / Avatar:
# “Interestingly, RNFL thickness was positively associated with some inflammatory markers, suggesting a link between inflammation and structural changes in the eye.”

# Visual Cue: Highlight RNFL thickness in diagram

# Scene 7  Immature Granulocytes

# Background: Spotlight on Immature Granulocytes

# On-Screen Text (0:37-0:42):
# Immature Granulocytes = Young white blood cells active in inflammation

# Voiceover / Avatar:
# “Among the markers, immature granulocytes—young white blood cells—showed the strongest relationship with IIH, potentially serving as an indicator of the condition.”

# Visual Cue: Spotlight on these cells

# Scene 8 Data Analysis / Summary

# Background: Researcher analyzing data, calm gesture toward camera

# On-Screen Text (0:43-0:50):
# Summary: Systemic inflammation may relate to IIH and eye structure changes

# Voiceover / Avatar:
# “This work suggests that systemic inflammation could be involved in IIH, helping us better understand how the condition affects the eyes and possibly guiding future research.”

# Visual Cue: Avatar gestures calmly to camera

# Scene 9  Closing

# Background: Calm, neutral

# Avatar: Avatar nodding slightly

# On-Screen Text (0:51-1:00):
# Reference: Sensoy et al., International Ophthalmology, 2026
# DOI: 10.1007/s10792-026-03996-x

# Voiceover / Avatar:
# “Sharing these findings helps the research community and clinicians explore new ways to study and monitor IIH. Thank you for taking a moment to learn about this work.”

# Visual Cue: Avatar speaking softly, open tone

# This version is HeyGen-ready:

# Linear, one scene after another.

# Clear on-screen text timing.

# Avatar speech / voiceover separated from text.

# Simple visual cues for AI to generate or animate.
# """

# # Use your existing avatar and a voice
# AVATAR_ID = "Angela-inblackskirt-20220820"  # Example professional female avatar
# VOICE_ID = "55f8c0f546884f9cbdefa113f5e7b682"  # Elizabeth - Friendly
# VOICE_NAME = "Elizabeth - Friendly"

# # Placeholder for text overlay (simple example, actual timed overlay may require template API)
# text_overlays = [
#     {"text": "Study Title: Early Cancer Detection", "start": 2, "end": 5}
# ]

# # -----------------------
# # 1) Create the video
# # -----------------------
# BASE_URL = "https://api.heygen.com/v2"
# headers = {"Content-Type": "application/json", "X-Api-Key": API_KEY}

# body = {
#     "video_inputs": [
#         {
#             "character": {
#                 "type": "avatar",
#                 "avatar_id": AVATAR_ID,
#                 "avatar_style": "normal"
#             },
#             "voice": {
#                 "type": "text",
#                 "input_text": script_text,
#                 "voice_id": VOICE_ID
#             }
#         }
#     ],
#     "dimension": {"width": 1080, "height": 1920},  # vertical for Reels/TikTok
#     "title": "IIH Clinical Explainer Video"
# }



# response = requests.post(f"{BASE_URL}/video/generate", headers=headers, json=body)
# try:
#     resp_json = response.json() if response.content else None
# except Exception as e:
#     raise RuntimeError(f"Invalid API response (status {response.status_code}): {e}") from e
# if resp_json is None:
#     raise RuntimeError(f"Invalid API response (status {response.status_code}): empty or non-JSON body")
# video_id = (resp_json.get("data") or {}).get("video_id")
# if not video_id:
#     err = resp_json.get("error")
#     msg = err.get("message", str(err)) if isinstance(err, dict) else str(err) if err else str(resp_json)
#     raise RuntimeError(f"Failed to start video generation: {msg}")
# print("Video generation started with ID:", video_id)

# # # # -----------------------
# # # # 2) Poll for completion
# # # # -----------------------
# # # status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
# # # print("Waiting for video to complete ...")
# # # while True:
# # #     status_resp = requests.get(status_url, headers=headers).json()
# # #     status = status_resp.get("status")
# # #     print("Status:", status)
# # #     if status == "completed":
# # #         download_url = status_resp["result"]["download_url"]
# # #         print("Video ready at:", download_url)
# # #         break
# # #     elif status == "failed":
# # #         raise RuntimeError("Video generation failed")
# # #     time.sleep(5)

# # # # -----------------------
# # # # 3) Download locally
# # # # -----------------------
# # # output_file = os.path.join(OUTPUT_DIR, "study_video.mp4")
# # # video_data = requests.get(download_url).content
# # # with open(output_file, "wb") as f:
# # #     f.write(video_data)

# # # print("Saved video locally to:", output_file)

