# Paper Search → Perplexity → Video Generation Integration

## Overview

Your `main.py` now has a complete integrated pipeline:

```
User Search Query
    ↓
Elasticsearch Agent (Paper Search)
    ↓
Perplexity AI (Script Generation)
    ↓
HeyGen (Video Generation)
    ↓
Generated Video File
```

## The Flow

### 1. **Paper Search (Elasticsearch)**
- Uses the `paper_search/seach_for_papers.py` module
- Calls Elasticsearch Agent Builder API
- Searches across indexed papers in your Elasticsearch cloud instance
- Returns matching papers with metadata

### 2. **Perplexity Analysis**
- Takes the top search result
- Sends paper data to Perplexity AI
- Generates a short, engaging script for the video
- Uses existing `analyze_with_perplexity()` function

### 3. **HeyGen Video Generation**
- Takes the Perplexity-generated script
- Creates a professional short-form video (vertical 9:16)
- Uses existing `generate_video_agent()` function
- Outputs MP4 file

## How to Run

### Option 1: Generate from Paper Index (Direct)
```bash
cd backend
python main.py --paper 0
python main.py --paper 5 --output my_custom_video.mp4
```

### Option 2: Generate from Search Query (Integrated Pipeline) ⭐
```bash
cd backend
python main.py --search "AI in cancer detection"
python main.py --search "machine learning brain imaging" --output research_video.mp4
python main.py --search "neural networks" --agent-id your-agent-id --output video.mp4
```

### Option 3: Python Script Usage
```python
from main import generate_video_from_search, generate_video_from_paper

# Search → Perplexity → Video (integrated)
result = generate_video_from_search("AI in surgery")
print(result['video_path'])  # /path/to/video.mp4
print(result['title'])        # Generated title
print(result['script'])       # Perplexity-generated script

# Direct paper index
generate_video_from_paper(paper_index=2)
```

## CLI Commands Breakdown

### Search with Integrated Pipeline
```bash
python main.py --search "your search query"
```
- Searches papers using Elasticsearch Agent
- Sends results to Perplexity for analysis
- Generates video with HeyGen
- Outputs: video file + metadata

### Search with Custom Output
```bash
python main.py --search "query" --output my_video.mp4
```
- Same as above but saves to custom filename

### Search with Custom Elasticsearch Agent
```bash
python main.py --search "query" --agent-id custom-agent-id
```
- Uses your custom Elasticsearch agent instead of default

### Direct Paper Index (Legacy)
```bash
python main.py --paper 5
```
- Skips search, goes directly to paper index
- Faster if you know which paper you want

## Required Environment Variables

For the search integration to work, you need:

```bash
# Elasticsearch (for paper search)
ELASTICSEARCH_URL=https://your-es-instance.es.us-central1.gcp.elastic.cloud
ELASTICSEARCH_API_KEY=your_api_key_here

# Perplexity (for script generation)
PERPLEXITY_API_KEY=your_key_here

# HeyGen (for video generation)
HEYGEN_API_KEY=your_key_here
```

Add these to your `.env` file in the backend directory.

## Output Example

When you run:
```bash
python main.py --search "neural networks"
```

You'll see:
```
================================================================================
🔍 INTEGRATED PIPELINE: Search → Perplexity → Video
================================================================================

🔍 Searching for papers: 'neural networks'...
✓ Search completed
Response: Found 5 papers related to neural networks...

📄 Using first search result...
Title: Deep Learning Architectures for Medical Imaging
Journal: Nature Machine Intelligence

🤖 Sending to Perplexity for analysis...
Script preview:
Neural networks have revolutionized medical imaging...

📝 Generating video title...
Title: Deep Learning in Medical Imaging: A Game-Changer

🎬 Generating HeyGen video...
✅ Video generated successfully!
📹 Saved to: heygen_videos/search_neural_networks.mp4

================================================================================
✅ PIPELINE COMPLETE:
  Search Query: neural networks
  Generated Title: Deep Learning in Medical Imaging: A Game-Changer
  Paper Source: Deep Learning Architectures for Medical Imaging
  Video Path: heygen_videos/search_neural_networks.mp4
================================================================================
```

## Code Location

The integration code is in:
- **Main script**: `backend/main.py`
- **Paper search module**: `paper_search/seach_for_papers.py`
- **Perplexity analysis**: `backend/perplexity_analysis.py`
- **Video generation**: `backend/heygen_agent.py`

## Key Functions in main.py

### `generate_video_from_search(search_query, agent_id, output_filename)`
```python
result = generate_video_from_search("AI in cancer detection")
# Returns: {
#   "video_path": "/path/to/video.mp4",
#   "title": "Generated video title",
#   "paper_title": "Original paper title",
#   "script": "Full Perplexity-generated script",
#   "search_query": "Your search query"
# }
```

### `generate_video_from_paper(paper_index, output_filename)`
```python
video_path = generate_video_from_paper(paper_index=0)
# Returns: "/path/to/video.mp4"
```

## Troubleshooting

### Error: "ELASTICSEARCH_API_KEY not set"
- Make sure your `.env` file has `ELASTICSEARCH_API_KEY` set
- Run from the `backend/` directory

### Error: "No papers found"
- Check your Elasticsearch connection
- Verify the agent ID is correct
- Falls back to local paper database if search fails

### Error: "ImportError: No module named paper_search"
- Make sure you're running from `backend/` directory
- The import path is already configured in main.py

## Example Full Workflow

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment (if using one)
source ../myenv/bin/activate  # or your venv

# 3. Run integrated pipeline
python main.py --search "machine learning in diagnostics" --output diagnostic_video.mp4

# Output: diagnostic_video.mp4 in heygen_videos/ folder
```

## Next Steps

1. **Set up Elasticsearch credentials** in `.env`
2. **Configure Elasticsearch agent** in Kibana
3. **Run the integrated pipeline** with your search query
4. **Check the generated video** in `heygen_videos/` folder
5. **Integrate with frontend** to trigger searches from UI

---

For more details on each component:
- See `paper_search/seach_for_papers.py` for search options
- See `backend/perplexity_analysis.py` for analysis types
- See `backend/heygen_agent.py` for video generation options
