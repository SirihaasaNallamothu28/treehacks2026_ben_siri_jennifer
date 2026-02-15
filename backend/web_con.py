import os
import asyncio
import requests
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRecorder
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("HEYGEN_API_KEY")


# async def connect_and_record(session_data, script_payload):

#     # 1️⃣ Create peer connection
#     pc = RTCPeerConnection()

#     # 2️⃣ Set up media recorder
#     # recorder = MediaRecorder("output.mp4")
#     recorder = MediaRecorder(os.path.join(os.path.dirname(__file__), "output.webm"))
#     recorder_started = False 

#     @pc.on("track")
#     def on_track(track):
#         nonlocal recorder_started
#         print("Track received:", track.kind)
#         recorder.addTrack(track)
#         if not recorder_started:
#             recorder_started = True
#             # start recording now that we have at least one track
#             asyncio.create_task(recorder.start())

#     # ✅ Set remote description so aiortc can parse the SDP
#     await pc.setRemoteDescription(offer)

#     # 4️⃣ Create and set local answer
#     answer = await pc.createAnswer()
#     await pc.setLocalDescription(answer)

#     # 5️⃣ Send local SDP back to HeyGen LiveAvatar
#     requests.post(
#         "https://api.heygen.com/v1/streaming.start",  # check the endpoint is correct for your session
#         headers={
#             "Authorization": f"Bearer {session_data['access_token']}",
#             "Content-Type": "application/json"
#         },
#         json={
#             "session_id": session_data['session_id'],
#             "sdp": {
#                 "sdp": pc.localDescription.sdp,
#                 "type": pc.localDescription.type
#             }
#         }
#     )

#     # 6️⃣ Start recording
#     await recorder.start()
#     print("Recording...")

#     # 7️⃣ Send script to LiveAvatar only AFTER SDP handshake is complete
#     # Example: Send your OSA script
#     requests.post(
#         "https://api.heygen.com/v1/interactive/script",
#         headers={
#             "Authorization": f"Bearer {session_data['access_token']}",
#             "Content-Type": "application/json"
#         },
#         json={
#             "session_id": session_data['session_id'],
#             "tasks": script_payload  # your script with title-on-screen instructions
#         }
#     )

#     # 8️⃣ Keep the recording alive long enough for the avatar to speak
#     await asyncio.sleep(105)  # ~1:45 video max

#     # 9️⃣ Stop recording and close connection
#     await recorder.stop()
#     await pc.close()
#     print("Recording saved to output.mp4")
async def connect_and_record(session_data):
    pc = RTCPeerConnection()
    recorder = MediaRecorder(os.path.join(os.path.dirname(__file__), "output.webm"))
    recorder_started = False

    @pc.on("track")
    def on_track(track):
        nonlocal recorder_started
        print("Track received:", track.kind)
        recorder.addTrack(track)
        if not recorder_started:
            recorder_started = True
            asyncio.create_task(recorder.start())
            print("Recorder started.")

    # SDP handshake
    offer = RTCSessionDescription(
        sdp=session_data["sdp"]["sdp"],
        type=session_data["sdp"]["type"]
    )
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send local SDP back to HeyGen
    requests.post(
        "https://api.heygen.com/v1/streaming.start",
        headers={
            "Authorization": f"Bearer {session_data['access_token']}",
            "Content-Type": "application/json"
        },
        json={
            "session_id": session_data['session_id'],
            "sdp": {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
        }
    )

    print("SDP handshake complete.")

    # Optional: skip sending a script if you don't want any on-screen tasks
    # requests.post(...)  # remove this block

    # Keep recording long enough
    await asyncio.sleep(105)

    await recorder.stop()
    await pc.close()
    print("Recording saved to output.webm")
