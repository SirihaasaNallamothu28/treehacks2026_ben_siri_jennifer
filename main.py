from heygen_agent import generate_video_agent

if __name__ == "__main__":



    prompt_text = """
    Speak the following text clearly and concisely in a calm, research-oriented voice. 
    Total speaking should be 45 seconds. Include 1-2 humorous/pop culture references (PO). 

    1. COVID-19 vaccines are safe for most, but rare side effects exist, like dangerous blood clots from adenovirus-based shots.
    2. Researchers found these vaccines triggered unusual immune reactions causing platelets to form clots.
    3. Understanding this helps doctors monitor patients and design safer vaccines.
    4. Overall, these side effects are extremely rare compared to the benefits of vaccination.
    5. Fun reference: It's like winning the lottery… but nobody wants this prize!
    6. Another: Imagine a plot twist in your favorite TV show—you didn’t expect it, but now you know why.

    On-screen captions should match key points:

    1. "Rare, dangerous side effects from some COVID-19 vaccines"
    2. "Cause: immune reaction triggers clot formation"
    3. "Why it matters: monitor patients & improve safety"
    4. "Extremely rare vs. benefits of vaccination"
    5. "Meme: ‘Winning the wrong lottery’"
    6. "Meme: ‘Unexpected plot twist’"
    7. "Reference: Vogel & Kupferschmidt, Science, 2026"
    """

    output = generate_video_agent(
        prompt=prompt_text,
        title="",
        output_path="original_long_covid.mp4"
    )

    print("Video generated:", output)

    clip = VideoFileClip(output_path)

    speed_factor = 2  # 2x speed; adjust as needed
    fast_clip = clip.fx(vfx.speedx, speed_factor)

    fast_video_path = "long_covid_generated_vid_meme.mp4"
    fast_clip.write_videofile(fast_video_path, codec="libx264", audio_codec="aac")

    print("Fast-forwarded video saved:", fast_video_path)







#     output = generate_ai_agent_video(
#         prompt = """
#         Here is a 30 second video script. Say speaking out loud part ands how the text on screen. 
# [
#     {
#         "speaking_out_loud": "Hi, today I’ll share findings on idiopathic intracranial hypertension, or IIH, where pressure inside the skull rises without a clear cause.",
#         "on_screen_text": "Inflammatory Markers in Idiopathic Intracranial Hypertension (IIH)",
#         "start_time": 0,
#         "end_time": 5
#     },
#     {
#         "speaking_out_loud": "This increased pressure can affect vision and cause headaches. Researchers studied whether inflammation plays a role in IIH.",
#         "on_screen_text": "IIH = Increased pressure inside the skull without known cause",
#         "start_time": 5,
#         "end_time": 10
#     },
#     {
#         "speaking_out_loud": "They examined the retinal nerve fiber layer, or RNFL, which sends visual signals to the brain, to see if it relates to inflammation.",
#         "on_screen_text": "RNFL = Retinal Nerve Fiber Layer",
#         "start_time": 10,
#         "end_time": 15
#     },
#     {
#         "speaking_out_loud": "Blood tests measured neutrophils, platelets, and immature granulocytes, along with combined markers called SII and SIRI.",
#         "on_screen_text": "Markers measured: Neutrophils, Platelets, Immature Granulocytes",
#         "start_time": 15,
#         "end_time": 20
#     },
#     {
#         "speaking_out_loud": "Patients with IIH had higher levels of these markers compared to healthy individuals.",
#         "on_screen_text": "Finding: Patients with IIH had higher inflammatory markers",
#         "start_time": 20,
#         "end_time": 22
#     },
#     {
#         "speaking_out_loud": "Thicker RNFL was positively associated with some inflammatory markers, suggesting a link between inflammation and eye structure changes.",
#         "on_screen_text": "Thicker RNFL correlated with higher inflammation",
#         "start_time": 22,
#         "end_time": 27
#     },
#     {
#         "speaking_out_loud": "Overall, systemic inflammation may be involved in IIH, helping us understand its effect on the eyes and guiding future research.",
#         "on_screen_text": "Systemic inflammation may relate to IIH and eye structure changes",
#         "start_time": 27,
#         "end_time": 29
#     },
#     {
#         "speaking_out_loud": "Reference: Sensoy et al., International Ophthalmology, 2026. Thank you for learning about this work.",
#         "on_screen_text": "Reference: Sensoy et al., Int. Ophthalmology, 2026",
#         "start_time": 29,
#         "end_time": 30
#     }
# ]
# """,

        
#         max_seconds=30,
#         avatar_id="Abigail_standing_office_front",
#         voice_id="55f8c0f546884f9cbdefa113f5e7b682",
#         title="IIH AI Agent Explainer",
#         output_path="iih_ai_agent.mp4",
#         on_screen_instruction="Display concise key phrases summarizing each major point."
#     )

#     print("Finished:", output)
