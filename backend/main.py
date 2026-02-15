
from live_avatar import create_session
from web_con import connect_and_record
from speak import send_script
import asyncio

# Import Perplexity analysis functions
from perplexity_analysis import (
    get_pmid_by_index,
    load_paper_json,
    analyze_with_perplexity,
    generate_video_title
)

# Import HeyGen video generation function  
from heygen_agent import generate_video_agent



def generate_video_from_paper(paper_index: int, output_filename: str = None):
    """
    Generate a HeyGen video from a research paper using Perplexity analysis.
    """
    print("=" * 80)
    print(f"Generating Video from Paper Index: {paper_index}")
    print("=" * 80)
    
    # 1. Get paper by index
    print(f"\n📄 Loading paper #{paper_index}...")
    pmid = get_pmid_by_index(paper_index)
    paper = load_paper_json(pmid)
    
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'][:3])}")
    print(f"Journal: {paper['journal']}")
    print(f"Year: {paper['publication_year']}")
    
    # 2. Generate short-form script
    print(f"\n🤖 Generating script with Perplexity...")
    script_text = analyze_with_perplexity(paper, "summarize_medium_text")
    
    print("Script preview:")
    print(script_text[:200] + "..." if len(script_text) > 200 else script_text)

    # 3. Generate clean short video title
    print("\n📝 Generating short video title...")
    video_title = generate_video_title(
        title=paper["title"],
        abstract=paper["abstract"]
    )

    print("Video title:", video_title)

    # 4. Build final HeyGen Video Agent prompt
    final_prompt = f"""
Create a professional short-form vertical explainer video.

TITLE:
{video_title}

SCRIPT:
{script_text}

Video requirements:
- Professional academic tone
- Clear and confident delivery
- Optimized for a 60-second vertical (9:16) format
- Keep pacing natural
- No filler language
"""

    # 5. Output filename
    if output_filename is None:
        output_filename = f"heygen_videos/paper_{paper_index}.mp4"

    print("\n🎬 Generating HeyGen Video Agent video...")

    video_path = generate_video_agent(
        prompt=final_prompt,
        title=video_title,
        output_path=output_filename,
    )
    
    print(f"\n✅ Video generated successfully!")
    print(f"📹 Saved to: {video_path}")
    
    return video_path
    

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        index = int(sys.argv[1])
    else:
        index = 0

    generate_video_from_paper(paper_index=index)



# from live_avatar import create_session
# from web_con import connect_and_record
# from speak import send_script
# import asyncio

# # Import Perplexity analysis functions
# from perplexity_analysis import (
#     get_pmid_by_index,
#     load_paper_json,
#     analyze_with_perplexity
# )

# # Import HeyGen video generation function  
# from heygen_agent import generate_video_agent



# def generate_video_from_paper(paper_index: int, output_filename: str = None):
#     """
#     Generate a HeyGen video from a research paper using Perplexity analysis.
    
#     Args:
#         paper_index (int): Index of the paper to analyze (from the dataset)
#         output_filename (str): Optional filename for the output video (defaults to paper_{index}.mp4)
    
#     Returns:
#         str: Path to the generated video file
#     """
#     print("=" * 80)
#     print(f"Generating Video from Paper Index: {paper_index}")
#     print("=" * 80)
    
#     # 1. Get paper by index
#     print(f"\n📄 Loading paper #{paper_index}...")
#     pmid = get_pmid_by_index(paper_index)
#     paper = load_paper_json(pmid)
    
#     print(f"Title: {paper['title']}")
#     print(f"Authors: {', '.join(paper['authors'][:3])}")
#     print(f"Journal: {paper['journal']}")
#     print(f"Year: {paper['publication_year']}")
    
#     # 2. Analyze with Perplexity to get JSON structure
#     print(f"\n🤖 Analyzing with Perplexity...")
#     analysis_json = analyze_with_perplexity(paper, "summarize_medium_json")
    
#     print(f"Analysis complete! Preview:")
#     print(analysis_json[:200] + "..." if len(analysis_json) > 200 else analysis_json)
    
#     # 3. Generate video with HeyGen
#     if output_filename is None:
#         output_filename = f"paper_{paper_index}.mp4"
    
#     print(f"\n🎬 Generating HeyGen video...")
    
#     # Parse the JSON string from Perplexity (strip markdown code fences if present)
#     import json
#     import re
    
#     # Remove markdown code fences if present
#     # cleaned_json = analysis_json.strip()
#     # if cleaned_json.startswith("```"):
#     #     # Remove ```json or ``` at start and ``` at end
#     #     cleaned_json = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_json)
#     #     cleaned_json = re.sub(r'\n?```\s*$', '', cleaned_json)
    
#     # body = json.loads(cleaned_json)
#         # Extract JSON block safely
#     cleaned_json = analysis_json.strip()

#     # Remove ALL markdown fences anywhere
#     cleaned_json = re.sub(r"```(?:json)?", "", cleaned_json)
#     cleaned_json = re.sub(r"```", "", cleaned_json)

# # Extract first JSON object only
#     match = re.search(r"\{.*\}", cleaned_json, re.DOTALL)
#     if not match:
#         raise ValueError("No valid JSON object found in response")

#     cleaned_json = match.group(0)

#     # Now parse
#     try:
#         body = json.loads(cleaned_json)
#     except json.JSONDecodeError as e:
#         print("❌ JSON ERROR:", e)
#         print("Problem area:")
#         print(cleaned_json[e.pos-120:e.pos+120])
#         raise

    
#     # Generate video using heygen_generator
#     video_path = generate_heygen_video_from_body(
#         body=body,
#         output_path=output_filename,
#         avatar_id="Abigail_expressive_2024112501",
#         voice_id="55f8c0f546884f9cbdefa113f5e7b682",
#     )
    
#     print(f"\n✅ Video generated successfully!")
#     print(f"📹 Saved to: {video_path}")
    
#     return video_path
    
# if __name__ == "__main__":
#     import sys

#     # Optional: allow passing index from command line
#     if len(sys.argv) > 1:
#         index = int(sys.argv[1])
#     else:
#         index = 0

#     generate_video_from_paper(paper_index=index)




# async def main():

#     script_payload = [
#         {
#             "text": "Imagine struggling to breathe at night because of obstructive sleep apnea, or OSA...",
#             "actions": [
#                 {"type": "display_text", "content": "Study: AI in OSA Diagnosis", "start_time": 0, "duration": 5}
#             ]
#         }
#     ]

#     task = asyncio.create_task(connect_and_record(session))
    
#     # Give it time to establish WebRTC connection
#     await asyncio.sleep(10)
    
#     # Send the script to the avatar
#     send_script(session, script_text)
    
#     # Wait for recording to finish
#     await task

# asyncio.run(main())


# ============================================================================
# EXAMPLE: Generate video from a research paper using Perplexity + HeyGen
# ============================================================================
# Uncomment the line below to generate a video from paper index 0
# video_path = generate_video_from_paper(paper_index=0, output_filename="my_research_video.mp4")


# from heygen_generator import generate_heygen_video_from_body
# import os
# import time
# import requests

# # -----------------------
# # CONFIG
# # -----------------------
# API_KEY = os.getenv("HEYGEN_API_KEY")  
# OUTPUT_DIR = "heygen_videos"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Your script
# script_text = """
# Today we discuss an important research study.
# Key topic: Early Cancer Detection.
# """

# # Use your existing avatar and a voice
# AVATAR_ID = "0e00fd99f2474e549b0df42e1a579cd9"  
# VOICE_ID = "73c0b6a2e29d4d38aca41454bf58c955" 

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
#     "dimension": {"width": 1080, "height": 1920},  # vertical for TikTok/Reels
#     "title": "Study Explainer Video"
# }

# response = requests.post(f"{BASE_URL}/video/generate", headers=headers, json=body)
# resp_json = response.json()
# video_id = resp_json.get("data", {}).get("video_id")
# if not video_id:
#     raise RuntimeError("Failed to start video generation")
# print("Video generation started with ID:", video_id)

# # -----------------------
# # 2) Poll for completion
# # -----------------------
# status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
# print("Waiting for video to complete ...")
# while True:
#     status_resp = requests.get(status_url, headers=headers).json()
#     status = status_resp.get("status")
#     print("Status:", status)
#     if status == "completed":
#         download_url = status_resp["result"]["download_url"]
#         print("Video ready at:", download_url)
#         break
#     elif status == "failed":
#         raise RuntimeError("Video generation failed")
#     time.sleep(5)

# # -----------------------
# # 3) Download locally
# # -----------------------
# output_file = os.path.join(OUTPUT_DIR, "study_video.mp4")
# video_data = requests.get(download_url).content
# with open(output_file, "wb") as f:
#     f.write(video_data)

# print("Saved video locally to:", output_file)


# me fr





# IRINOTECAN_BODY = {
#     "title": "Single-Cell Insights into Irinotecan Resistance in Colorectal Cancer",
#     "caption": True,
#     "video_inputs": [
#         {
#             "character": {
#                 "type": "avatar",
#                 "avatar_id": "{{AVATAR_ID}}",
#                 "avatar_style": "normal"
#             },
#             "voice": {
#                 "type": "text",
#                 "voice_id": "{{VOICE_ID}}",
#                 "input_text": "Irinotecan is a standard treatment for metastatic colorectal cancer, but up to half of patients develop resistance. This study investigates why that happens at single-cell resolution."
#             },
#             "background": {"type": "color", "value": "#FFFFFF"},
#             "text": {
#                 "type": "text",
#                 "text": "Irinotecan Resistance\n30–50% of mCRC Patients",
#                 "font_size": 60,
#                 "font_weight": "bold",
#                 "color": "#000000",
#                 "position": {"x": 0.5, "y": 0.5},
#                 "text_align": "center",
#                 "line_height": 1.2,
#                 "width": 1400
#             }
#         },
#         {
#             "character": {
#                 "type": "avatar",
#                 "avatar_id": "{{AVATAR_ID}}",
#                 "avatar_style": "normal"
#             },
#             "voice": {
#                 "type": "text",
#                 "voice_id": "{{VOICE_ID}}",
#                 "input_text": "Researchers built patient-derived organoid models from resistant and sensitive tumors and performed single-cell RNA sequencing on over twelve thousand cells."
#             },
#             "background": {"type": "color", "value": "#FFFFFF"},
#             "text": {
#                 "type": "text",
#                 "text": "Patient-Derived Organoids\n12,360 Cells Sequenced",
#                 "font_size": 60,
#                 "font_weight": "bold",
#                 "color": "#000000",
#                 "position": {"x": 0.5, "y": 0.5},
#                 "text_align": "center",
#                 "line_height": 1.2,
#                 "width": 1400
#             }
#         },
#         {
#             "character": {
#                 "type": "avatar",
#                 "avatar_id": "{{AVATAR_ID}}",
#                 "avatar_style": "normal"
#             },
#             "voice": {
#                 "type": "text",
#                 "voice_id": "{{VOICE_ID}}",
#                 "input_text": "They identified two resistant cell clusters. One showed Wnt pathway activation and stem-like features, while the other was enriched for lipid metabolism and Notch signaling."
#             },
#             "background": {"type": "color", "value": "#FFFFFF"},
#             "text": {
#                 "type": "text",
#                 "text": "Cluster 1: Wnt + Stemness\nCluster 6: Lipid + Notch",
#                 "font_size": 60,
#                 "font_weight": "bold",
#                 "color": "#000000",
#                 "position": {"x": 0.5, "y": 0.5},
#                 "text_align": "center",
#                 "line_height": 1.2,
#                 "width": 1400
#             }
#         },
#         {
#             "character": {
#                 "type": "avatar",
#                 "avatar_id": "{{AVATAR_ID}}",
#                 "avatar_style": "normal"
#             },
#             "voice": {
#                 "type": "text",
#                 "voice_id": "{{VOICE_ID}}",
#                 "input_text": "Together, these pathways drive resistance. Targeting Wnt signaling and the lipid-Notch axis could enable new combination therapies for colorectal cancer."
#             },
#             "background": {"type": "color", "value": "#FFFFFF"},
#             "text": {
#                 "type": "text",
#                 "text": "Target Wnt + Lipid-Notch\nNew Combination Strategies",
#                 "font_size": 60,
#                 "font_weight": "bold",
#                 "color": "#000000",
#                 "position": {"x": 0.5, "y": 0.5},
#                 "text_align": "center",
#                 "line_height": 1.2,
#                 "width": 1400
#             }
#         }
#     ],
#     "dimension": {"width": "{{WIDTH}}", "height": "{{HEIGHT}}"}
# }


# def main():
#     output_path = "irinotecan_resistance_video.mp4"
#     generate_heygen_video_from_body(
#         body=IRINOTECAN_BODY,
#         output_path=output_path,
#         avatar_id="Abigail_standing_office_front",
#         voice_id="55f8c0f546884f9cbdefa113f5e7b682",
#         width=1080,
#         height=1920,
#     )
#     print("Finished:", output_path)


# if __name__ == "__main__":
#     main()
