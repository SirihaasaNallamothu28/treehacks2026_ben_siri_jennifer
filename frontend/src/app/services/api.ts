/**
 * Simple API service to communicate with the backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface VideoJob {
  job_id: string;
  status: "queued" | "generating" | "completed" | "failed";
  message: string;
  paper_index: number;
  created_at: string;
  video_path: string | null;
  title: string | null;
  metadata: {
    citations: number;
    year: number | string;
    journal: string;
  } | null;
  completed_at?: string;
  error?: string;
}

/**
 * Start video generation for a paper.
 */
export async function generateVideo(paperIndex: number = 14): Promise<VideoJob> {
  const response = await fetch(`${API_BASE_URL}/api/generate-video`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      paper_index: paperIndex,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to start video generation: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Poll for video generation status.
 */
export async function getVideoStatus(jobId: string): Promise<VideoJob> {
  const response = await fetch(`${API_BASE_URL}/api/video-status/${jobId}`);

  if (!response.ok) {
    throw new Error(`Failed to get video status: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Poll until video is complete or failed.
 * Calls onProgress callback with status updates.
 */
export async function pollVideoUntilComplete(
  jobId: string,
  onProgress?: (job: VideoJob) => void,
  intervalMs: number = 3000
): Promise<VideoJob> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const job = await getVideoStatus(jobId);

        // Call progress callback
        if (onProgress) {
          onProgress(job);
        }

        // Check if done
        if (job.status === "completed") {
          resolve(job);
        } else if (job.status === "failed") {
          reject(new Error(job.error || "Video generation failed"));
        } else {
          // Continue polling
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}
