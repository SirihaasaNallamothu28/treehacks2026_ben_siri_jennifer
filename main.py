from heygen_generator import generate_heygen_video_from_body

IRINOTECAN_BODY = {
    "title": "Single-Cell Insights into Irinotecan Resistance in Colorectal Cancer",
    "caption": True,
    "video_inputs": [
        {
            "character": {
                "type": "avatar",
                "avatar_id": "{{AVATAR_ID}}",
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "voice_id": "{{VOICE_ID}}",
                "input_text": "Irinotecan is a standard treatment for metastatic colorectal cancer, but up to half of patients develop resistance. This study investigates why that happens at single-cell resolution."
            },
            "background": {"type": "color", "value": "#FFFFFF"},
            "text": {
                "type": "text",
                "text": "Irinotecan Resistance\n30–50% of mCRC Patients",
                "font_size": 60,
                "font_weight": "bold",
                "color": "#000000",
                "position": {"x": 0.5, "y": 0.5},
                "text_align": "center",
                "line_height": 1.2,
                "width": 1400
            }
        },
        {
            "character": {
                "type": "avatar",
                "avatar_id": "{{AVATAR_ID}}",
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "voice_id": "{{VOICE_ID}}",
                "input_text": "Researchers built patient-derived organoid models from resistant and sensitive tumors and performed single-cell RNA sequencing on over twelve thousand cells."
            },
            "background": {"type": "color", "value": "#FFFFFF"},
            "text": {
                "type": "text",
                "text": "Patient-Derived Organoids\n12,360 Cells Sequenced",
                "font_size": 60,
                "font_weight": "bold",
                "color": "#000000",
                "position": {"x": 0.5, "y": 0.5},
                "text_align": "center",
                "line_height": 1.2,
                "width": 1400
            }
        },
        {
            "character": {
                "type": "avatar",
                "avatar_id": "{{AVATAR_ID}}",
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "voice_id": "{{VOICE_ID}}",
                "input_text": "They identified two resistant cell clusters. One showed Wnt pathway activation and stem-like features, while the other was enriched for lipid metabolism and Notch signaling."
            },
            "background": {"type": "color", "value": "#FFFFFF"},
            "text": {
                "type": "text",
                "text": "Cluster 1: Wnt + Stemness\nCluster 6: Lipid + Notch",
                "font_size": 60,
                "font_weight": "bold",
                "color": "#000000",
                "position": {"x": 0.5, "y": 0.5},
                "text_align": "center",
                "line_height": 1.2,
                "width": 1400
            }
        },
        {
            "character": {
                "type": "avatar",
                "avatar_id": "{{AVATAR_ID}}",
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "voice_id": "{{VOICE_ID}}",
                "input_text": "Together, these pathways drive resistance. Targeting Wnt signaling and the lipid-Notch axis could enable new combination therapies for colorectal cancer."
            },
            "background": {"type": "color", "value": "#FFFFFF"},
            "text": {
                "type": "text",
                "text": "Target Wnt + Lipid-Notch\nNew Combination Strategies",
                "font_size": 60,
                "font_weight": "bold",
                "color": "#000000",
                "position": {"x": 0.5, "y": 0.5},
                "text_align": "center",
                "line_height": 1.2,
                "width": 1400
            }
        }
    ],
    "dimension": {"width": "{{WIDTH}}", "height": "{{HEIGHT}}"}
}


def main():
    output_path = "irinotecan_resistance_video.mp4"
    generate_heygen_video_from_body(
        body=IRINOTECAN_BODY,
        output_path=output_path,
        avatar_id="Abigail_standing_office_front",
        voice_id="55f8c0f546884f9cbdefa113f5e7b682",
        width=1080,
        height=1920,
    )
    print("Finished:", output_path)


if __name__ == "__main__":
    main()
