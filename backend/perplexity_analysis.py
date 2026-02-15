import json
import os
from pathlib import Path
from perplexity import Perplexity
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Initialize Perplexity client
client = Perplexity()

def get_pmid_by_index(index):
    """
    Get PMID from output_pmc_papers directory by index.

    Args:
        index: Integer index into the sorted list of PMID files

    Returns:
        String PMID (e.g., "41678069")
    """
    # Path to output_pmc_papers in parent directory
    output_dir = Path(__file__).parent.parent / "output_pmc_papers"
    json_files = sorted(output_dir.glob("PMID_*.json"))

    if index < 0 or index >= len(json_files):
        raise IndexError(f"Index {index} out of range. Available: 0-{len(json_files)-1}")

    # Extract PMID from filename: "PMID_41678069.json" -> "41678069"
    filename = json_files[index].stem  # Gets "PMID_41678069"
    pmid = filename.replace("PMID_", "")  # Gets "41678069"

    return pmid

def load_paper_json(pmid):
    """Load a paper JSON file by PMID"""
    # Path to output_pmc_papers in parent directory
    json_file = Path(__file__).parent.parent / "output_pmc_papers" / f"PMID_{pmid}.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_video_title(title, abstract):
    """
    Generate a simplified, engaging title for a short-form video based on the research paper.

    Args:
        title: Original paper title
        abstract: Paper abstract

    Returns:
        String title (40-70 characters) suitable for short-form video
    """
    TITLE_STYLE_GUIDE = """You are creating a catchy, accessible title for a short medical research video.

Your target audience is students new to healthcare who are curious about the latest medical research.

Guidelines:
- Use simple, everyday language - avoid medical jargon
- Make it engaging and intriguing
- Focus on the key finding or "what" rather than the technical "how"
- Keep it between 40-70 characters (strict requirement)
- Make it sound interesting without being clickbait
- Use active language when possible

Examples of good transformations:
- "Artificial intelligence in surgical planning..." → "AI Helps Predict Sleep Apnea Surgery Success"
- "Risk assessment of cardiovascular disease..." → "New Tool Predicts Heart Disease Risk Earlier"
- "Novel therapeutic approach for neuroinflammation..." → "Fresh Take on Treating Brain Inflammation"
"""

    prompt = f"""{TITLE_STYLE_GUIDE}

Original paper title: "{title}"

Paper abstract (for context):
"{abstract}"

Create a single, engaging video title that captures the essence of this research. The title MUST be between 40-70 characters.

Return ONLY the title text, nothing else. No quotes, no explanations."""

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=False
    )

    video_title = response.choices[0].message.content.strip()

    # Remove quotes if present
    video_title = video_title.strip('"\'')

    return video_title

def analyze_with_perplexity(paper_data, analysis_type="summarize_short_json"):
    """
    Analyze a paper using Perplexity
    
    Args:
        paper_data: Dictionary containing paper metadata and abstract (full paper not in current dataset)
        analysis_type: Type of analysis
            - "summarize_short_json": Short video script (30-40 sec)
            - "summarize_short_text": Short video script (30-40 sec, plain text)
            - "summarize_medium_json": Medium video script (1 min)
            - "summarize_medium_text": Medium video script (1 min, plain text)
            - "key_findings", "clinical_relevance", etc.
    """

    title = paper_data.get("title", "")
    abstract = paper_data.get("abstract", "")
    journal = paper_data.get("journal", "")
    pub_year = paper_data.get("publication_year", "")

    # === SHARED STYLE GUIDELINES ===
    STYLE_GUIDE = """You are a medical research video script planner.

Your target audience is students new to healthcare who are curious about the latest medical research. Write in simple, everyday language - avoid medical jargon when possible.
For example, use "eardrum" instead of "tympanic membrane" and "a type of cancer" instead of "sarcomas."

In the overall script, focus primarily on:
- Keep spoken lines short (1–2 sentences max per scene).
- On-screen text should be concise and visually readable (not paragraphs).
- Tone: professional but engaging, suitable for a live demo.

Try to answer the following focus questions, but prioritize the content and flow of the research story:
- The medical findings and what researchers discovered
- Why this matters for patients and healthcare
- How the study was conducted (briefly)

If the paper involves AI or computational methods, or if you identify a potential application for AI in the research,
briefly mention  this as a supporting detail - but keep the focus on the medical significance and results, not the technology itself.

Write in a conversational narrative style that tells the story of the research, rather than answering questions in a rigid format. Make it engaging and accessible."""

    SCENE_FORMAT = """
        For each scene, define:
        1. What the avatar will say aloud.
        2. What text should appear on screen.
    """

    TEXT_FORMAT = """
Return only the script text. No JSON. No explanations. Just the narration script that would be spoken in the video."""

    prompts = {
        "summarize_short_json": f"""{STYLE_GUIDE}

Given this paper abstract:

"{abstract}"

Create a natural, engaging script for a 30-40 second video (60-85 words) that is split into 2 to 3 scenes which follow the flow of the research.

Keep the total word count between 60-85 words for approximately 30-40 seconds of speaking time.

{SCENE_FORMAT}
    
Keep the total word count of the script between 60-85 words.
{TEXT_FORMAT}""",

        "summarize_short_text": f"""{STYLE_GUIDE}

Given this paper abstract:

"{abstract}"

Create a natural, engaging script for a 30-40 second video (60-85 words) that follows the flow of the research.

Keep the total word count between 60-85 words.
{TEXT_FORMAT}""",

        "summarize_medium_json": f"""{STYLE_GUIDE}

Given this paper abstract:

"{abstract}"

Create a natural, engaging script for a 1-minute video (130-160 words) that is split into 3 to 5 scenes which follow the flow of the research.

{SCENE_FORMAT}

Keep the total word count of the script between 130-160 words.
{TEXT_FORMAT}""",

        "summarize_medium_text": f"""{STYLE_GUIDE}

Given this paper abstract:

"{abstract}"

Create a natural, engaging script for a 1-minute video (130-160 words) that follows the flow of the research.

Keep the total word count between 130-160 words.
{TEXT_FORMAT}""",

        "key_findings": f"""What are the main findings and conclusions from this research?

Title: {title}

Abstract:
{abstract}""",

        "clinical_relevance": f"""What is the clinical significance and potential real-world application of this research?

Title: {title}

Abstract:
{abstract}""",

        "methodology": f"""Describe the research methodology and approach used in this study:

Title: {title}

Abstract:
{abstract}""",

        "limitations": f"""What are the limitations and potential biases mentioned or implied in this study?

Title: {title}

Abstract:
{abstract}""",

        "video_agent_prompt": f"""{STYLE_GUIDE}

Given this paper abstract:
"{abstract}"

Create an engaging video prompt for a 1-minute medical research explainer video.

The prompt should:
1. Start with the main script/narration (130-160 words)
2. Include suggestions for text overlays at key moments (e.g., "TEXT OVERLAY at 0:05: 'Study Focus: Sleep Apnea'")
3. Be written in a way that a video AI agent can understand and execute

Format example:
"Create a 1-minute video about {{topic}}. 

SCRIPT:
{{Your narration script here}}

SUGGESTED TEXT OVERLAYS:
- At 0:00-0:05: '{{overlay text}}'
- At 0:15-0:20: '{{overlay text}}'
"

Focus on making this a clear, executable prompt that tells the video agent exactly what to create.
{TEXT_FORMAT}"""
    }

    prompt = prompts.get(analysis_type, prompts["summarize_short_json"])

    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=False
    )

    return response.choices[0].message.content

def batch_analyze_papers(limit=5, analysis_type="summarize_short_json"):
    """Analyze multiple papers from the output directory"""
    output_dir = Path(__file__).parent.parent / "output_pmc_papers"
    json_files = list(output_dir.glob("PMID_*.json"))[:limit]

    results = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            paper_data = json.load(f)

        print(f"\n{'='*80}")
        print(f"Analyzing: {paper_data['title'][:60]}...")
        print(f"PMID: {paper_data['pmid']}")
        print(f"{'='*80}")

        analysis = analyze_with_perplexity(paper_data, analysis_type)
        print(f"\n{analysis}\n")

        results.append({
            "pmid": paper_data["pmid"],
            "title": paper_data["title"],
            "analysis": analysis
        })

    return results





# import json
# import os
# from pathlib import Path
# from perplexity import Perplexity
# from dotenv import load_dotenv

# # Load environment variables from parent directory
# load_dotenv(Path(__file__).parent.parent / ".env")

# # Initialize Perplexity client
# client = Perplexity()

# def get_pmid_by_index(index):
#     """
#     Get PMID from output_pmc_papers directory by index.

#     Args:
#         index: Integer index into the sorted list of PMID files

#     Returns:
#         String PMID (e.g., "41678069")
#     """
#     # Path to output_pmc_papers in parent directory
#     output_dir = Path(__file__).parent.parent / "output_pmc_papers"
#     json_files = sorted(output_dir.glob("PMID_*.json"))

#     if index < 0 or index >= len(json_files):
#         raise IndexError(f"Index {index} out of range. Available: 0-{len(json_files)-1}")

#     # Extract PMID from filename: "PMID_41678069.json" -> "41678069"
#     filename = json_files[index].stem  # Gets "PMID_41678069"
#     pmid = filename.replace("PMID_", "")  # Gets "41678069"

#     return pmid

# def load_paper_json(pmid):
#     """Load a paper JSON file by PMID"""
#     # Path to output_pmc_papers in parent directory
#     json_file = Path(__file__).parent.parent / "output_pmc_papers" / f"PMID_{pmid}.json"
#     with open(json_file, 'r', encoding='utf-8') as f:
#         return json.load(f)

# def generate_video_title(title, abstract):
#     """
#     Generate a simplified, engaging title for a short-form video based on the research paper.

#     Args:
#         title: Original paper title
#         abstract: Paper abstract

#     Returns:
#         String title (40-70 characters) suitable for short-form video
#     """
#     TITLE_STYLE_GUIDE = """You are creating a catchy, accessible title for a short medical research video.

# Your target audience is students new to healthcare who are curious about the latest medical research.

# Guidelines:
# - Use simple, everyday language - avoid medical jargon
# - Make it engaging and intriguing
# - Focus on the key finding or "what" rather than the technical "how"
# - Keep it between 40-70 characters (strict requirement)
# - Make it sound interesting without being clickbait
# - Use active language when possible

# Examples of good transformations:
# - "Artificial intelligence in surgical planning..." → "AI Helps Predict Sleep Apnea Surgery Success"
# - "Risk assessment of cardiovascular disease..." → "New Tool Predicts Heart Disease Risk Earlier"
# - "Novel therapeutic approach for neuroinflammation..." → "Fresh Take on Treating Brain Inflammation"
# """

#     prompt = f"""{TITLE_STYLE_GUIDE}

# Original paper title: "{title}"

# Paper abstract (for context):
# "{abstract}"

# Create a single, engaging video title that captures the essence of this research. The title MUST be between 40-70 characters.

# Return ONLY the title text, nothing else. No quotes, no explanations."""

#     response = client.chat.completions.create(
#         model="sonar-pro",
#         messages=[
#             {"role": "user", "content": prompt}
#         ],
#         stream=False
#     )

#     video_title = response.choices[0].message.content.strip()

#     # Remove quotes if present
#     video_title = video_title.strip('"\'')

#     return video_title

# def analyze_with_perplexity(paper_data, analysis_type="summarize_short_json"):
#     """
#     Analyze a paper using Perplexity

#     Args:
#         paper_data: Dictionary containing paper metadata and abstract (full paper not in current dataset)
#         analysis_type: Type of analysis
#             - "summarize_short_json": Short video script (30-40 sec, JSON format)
#             - "summarize_short_text": Short video script (30-40 sec, plain text)
#             - "summarize_medium_json": Medium video script (1 min, JSON format)
#             - "summarize_medium_text": Medium video script (1 min, plain text)
#             - "key_findings", "clinical_relevance", etc.
#     """

#     title = paper_data.get("title", "")
#     abstract = paper_data.get("abstract", "")
#     journal = paper_data.get("journal", "")
#     pub_year = paper_data.get("publication_year", "")

#     # === SHARED STYLE GUIDELINES ===
#     # Edit this section to change the linguistic style and content focus for all summarize prompts
#     STYLE_GUIDE = """You are a medical research video script planner.

# Your target audience is students new to healthcare who are curious about the latest medical research. Write in simple, everyday language - avoid medical jargon when possible.
# For example, use "eardrum" instead of "tympanic membrane" and "a type of cancer" instead of "sarcomas."

# In the overall script, focus primarily on:
# - Keep spoken lines short (1–2 sentences max per scene).
# - On-screen text should be concise and visually readable (not paragraphs).
# - Tone: professional but engaging, suitable for a live demo.

# Try to answer the following focus questions, but prioritize the content and flow of the research story:
# - The medical findings and what researchers discovered
# - Why this matters for patients and healthcare
# - How the study was conducted (briefly)

# If the paper involves AI or computational methods, or if you identify a potential application for AI in the research,
# briefly mention this as a supporting detail - but keep the focus on the medical significance and results, not the technology itself.

# Write in a conversational narrative style that tells the story of the research, rather than answering questions in a rigid format. Make it engaging and accessible."""

#     # === SCENE FORMAT SPECIFICATIONS ===
#     SCENE_FORMAT = """
#         For each scene, define:
#         1. What the avatar will say aloud (voice.input_text).
#         2. What text should appear on screen (text.text).
#     """

#     # === OUTPUT FORMAT SPECIFICATIONS ===
    





#     TEXT_FORMAT = """
# Return only the script text. No JSON. No explanations. Just the narration script that would be spoken in the video."""

#     # Create different prompts based on analysis type
#     prompts = {
#         "summarize_short_json": f"""{STYLE_GUIDE}

# Given this paper abstract:

# "{abstract}"

# Create a natural, engaging script for a 30-40 second video (60-85 words) that is split into 2 to 3 scenes which follow the flow of the research.

# Keep the total word count between 60-85 words for approximately 30-40 seconds of speaking time.

# {SCENE_FORMAT}
    
# Keep the total word count of the script between 60-85 words.
# {JSON_FORMAT}""",

#         "summarize_short_text": f"""{STYLE_GUIDE}

# Given this paper abstract:

# "{abstract}"

# Create a natural, engaging script for a 30-40 second video (60-85 words) that follows the flow of the research.

# Keep the total word count between 60-85 words.
# {TEXT_FORMAT}""",

#         "summarize_medium_json": f"""{STYLE_GUIDE}

# Given this paper abstract:

# "{abstract}"

# Create a natural, engaging script for a 1-minute video (130-160 words) that is split into 3 to 5 scenes which follow the flow of the research.

# {SCENE_FORMAT}

# Keep the total word count of the script between 130-160 words.
# {JSON_FORMAT}""",

#         "summarize_medium_text": f"""{STYLE_GUIDE}

# Given this paper abstract:

# "{abstract}"

# Create a natural, engaging script for a 1-minute video (130-160 words) that follows the flow of the research.

# Keep the total word count between 130-160 words.
# {TEXT_FORMAT}""",

#         "key_findings": f"""What are the main findings and conclusions from this research?

# Title: {title}

# Abstract:
# {abstract}""",

#         "clinical_relevance": f"""What is the clinical significance and potential real-world application of this research?

# Title: {title}

# Abstract:
# {abstract}""",

#         "methodology": f"""Describe the research methodology and approach used in this study:

# Title: {title}

# Abstract:
# {abstract}""",

#         "limitations": f"""What are the limitations and potential biases mentioned or implied in this study?

# Title: {title}

# Abstract:
# {abstract}""",

#         "video_agent_prompt": f"""{STYLE_GUIDE}

# Given this paper abstract:
# "{abstract}"

# Create an engaging video prompt for a 1-minute medical research explainer video.

# The prompt should:
# 1. Start with the main script/narration (130-160 words)
# 2. Include suggestions for text overlays at key moments (e.g., "TEXT OVERLAY at 0:05: 'Study Focus: Sleep Apnea'")
# 3. Be written in a way that a video AI agent can understand and execute

# Format example:
# "Create a 1-minute video about {{topic}}. 

# SCRIPT:
# {{Your narration script here}}

# SUGGESTED TEXT OVERLAYS:
# - At 0:00-0:05: '{{overlay text}}'
# - At 0:15-0:20: '{{overlay text}}'
# "

# Focus on making this a clear, executable prompt that tells the video agent exactly what to create.
# {TEXT_FORMAT}"""
#     }

#     prompt = prompts.get(analysis_type, prompts["summarize_short_json"])

#     # Call Perplexity API
#     response = client.chat.completions.create(
#         model="sonar-pro",
#         messages=[
#             {"role": "user", "content": prompt}
#         ],
#         stream=False
#     )

#     return response.choices[0].message.content

# def batch_analyze_papers(limit=5, analysis_type="summarize_short_json"):
#     """Analyze multiple papers from the output directory"""
#     # Path to output_pmc_papers in parent directory
#     output_dir = Path(__file__).parent.parent / "output_pmc_papers"
#     json_files = list(output_dir.glob("PMID_*.json"))[:limit]

#     results = []
#     for json_file in json_files:
#         with open(json_file, 'r', encoding='utf-8') as f:
#             paper_data = json.load(f)

#         print(f"\n{'='*80}")
#         print(f"Analyzing: {paper_data['title'][:60]}...")
#         print(f"PMID: {paper_data['pmid']}")
#         print(f"{'='*80}")

#         analysis = analyze_with_perplexity(paper_data, analysis_type)
#         print(f"\n{analysis}\n")

#         results.append({
#             "pmid": paper_data["pmid"],
#             "title": paper_data["title"],
#             "analysis": analysis
#         })

#     return results
