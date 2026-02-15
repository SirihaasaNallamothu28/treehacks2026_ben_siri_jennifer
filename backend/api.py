"""
Simple FastAPI backend to connect frontend to HeyGen video generation.
Keeps it minimal - just what we need to generate and serve videos.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from typing import Optional, Dict
from datetime import datetime

# Import our video generation function
from main import generate_video_from_paper
from perplexity_analysis import get_pmid_by_index, load_paper_json

app = FastAPI()

# Enable CORS so frontend can talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated videos as static files
# Make sure the directory exists
os.makedirs("heygen_videos", exist_ok=True)
app.mount("/heygen_videos", StaticFiles(directory="heygen_videos"), name="heygen_videos")

# In-memory storage for video generation status
# In production, you'd use a database
video_jobs: Dict[str, dict] = {}


class GenerateVideoRequest(BaseModel):
    paper_index: int = 14  # Default to paper 14 as requested
    user_interests: Optional[str] = None


def background_video_generation(job_id: str, paper_index: int):
    """
    Background task to generate video.
    Updates job status as it progresses with detailed messages.
    """
    try:
        # Step 1: Loading paper
        video_jobs[job_id]["status"] = "generating"
        video_jobs[job_id]["message"] = f"📄 Loading paper #{paper_index}..."
        print(f"[{job_id}] Loading paper {paper_index}")

        pmid = get_pmid_by_index(paper_index)
        paper = load_paper_json(pmid)

        # Update metadata
        video_jobs[job_id]["title"] = paper.get("title", "Unknown Title")
        video_jobs[job_id]["paper_index"] = paper_index
        video_jobs[job_id]["metadata"] = {
            "citations": paper.get("citation_count", 0),
            "year": paper.get("publication_year", "Unknown"),
            "journal": paper.get("journal", "Unknown Journal"),
        }

        # Step 2: Analyzing with Perplexity
        video_jobs[job_id]["message"] = "🤖 Analyzing paper with Perplexity AI..."
        print(f"[{job_id}] Analyzing with Perplexity")

        # Step 3: Generating script
        video_jobs[job_id]["message"] = "✍️ Generating video script..."
        print(f"[{job_id}] Generating script")

        # Step 4: Creating video title
        video_jobs[job_id]["message"] = "📝 Creating video title..."
        print(f"[{job_id}] Creating title")

        # Step 5: Sending to HeyGen
        video_jobs[job_id]["message"] = "🎬 Sending to HeyGen for video generation..."
        print(f"[{job_id}] Sending to HeyGen")

        # Generate the video
        output_path = f"heygen_videos/paper_{paper_index}.mp4"

        # Step 6: HeyGen is processing
        video_jobs[job_id]["message"] = "⏳ HeyGen is generating your video (this may take 2-5 minutes)..."
        print(f"[{job_id}] HeyGen processing...")

        video_path = generate_video_from_paper(paper_index, output_path)

        # Step 7: Downloading video
        video_jobs[job_id]["message"] = "⬇️ Downloading video..."
        print(f"[{job_id}] Downloading video")

        # Mark as complete
        video_jobs[job_id]["status"] = "completed"
        video_jobs[job_id]["video_path"] = video_path
        video_jobs[job_id]["message"] = "✅ Video ready!"
        video_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        print(f"[{job_id}] ✅ Completed! Video at: {video_path}")

    except Exception as e:
        video_jobs[job_id]["status"] = "failed"
        video_jobs[job_id]["error"] = str(e)
        video_jobs[job_id]["message"] = f"❌ Failed: {str(e)}"
        print(f"[{job_id}] ❌ Error: {e}")


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Synapsis API is running"}


@app.post("/api/generate-video")
def generate_video(request: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    Start video generation in the background.
    Returns a job_id that can be used to poll for status.
    """
    # Create a unique job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.paper_index}"

    # Initialize job status
    video_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation queued...",
        "paper_index": request.paper_index,
        "created_at": datetime.now().isoformat(),
        "video_path": None,
        "title": None,
        "metadata": None,
    }

    # Start background task
    background_tasks.add_task(background_video_generation, job_id, request.paper_index)

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Video generation started"
    }


@app.get("/api/video-status/{job_id}")
def get_video_status(job_id: str):
    """
    Check the status of a video generation job.
    Frontend will poll this endpoint.
    """
    if job_id not in video_jobs:
        return JSONResponse(
            status_code=404,
            content={"error": "Job not found"}
        )

    return video_jobs[job_id]


@app.get("/api/list-jobs")
def list_jobs():
    """
    List all video generation jobs.
    Useful for debugging.
    """
    return {"jobs": list(video_jobs.values())}


if __name__ == "__main__":
    import uvicorn
    # Run on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
