// API client for backend communication
export interface VideoData {
  id: string;
  title: string;
  originalTitle: string;
  description: string;
  videoPath: string;
  relevanceBadge: string;
  metadata: {
    citations: number;
    year: number;
    journal: string;
  };
  studyData: {
    datasetSize: string;
    trialSize: string;
    modality: string;
    modelType: string;
    evaluationMetric: string;
    studyType: string;
  };
  results: {
    auroc?: string;
    pValue?: string;
    sensitivity?: string;
    specificity?: string;
    improvement?: string;
  };
}

export interface PaperData {
  id: string;
  pmid: string;
  title: string;
  abstract: string;
  authors: string[];
  journal: string;
  year: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const apiClient = {
  // Fetch all available videos
  getVideos: async (): Promise<VideoData[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/videos`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch videos:", error);
      return [];
    }
  },

  // Fetch a specific video by ID
  getVideo: async (id: string): Promise<VideoData | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/videos/${id}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch video ${id}:`, error);
      return null;
    }
  },

  // Fetch papers
  getPapers: async (): Promise<PaperData[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/papers`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to fetch papers:", error);
      return [];
    }
  },

  // Fetch a specific paper by ID
  getPaper: async (id: string): Promise<PaperData | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/papers/${id}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Failed to fetch paper ${id}:`, error);
      return null;
    }
  },

  // Generate a new video from paper index
  generateVideo: async (
    paperIndex: number,
    interests: string[],
    strengths: string[]
  ): Promise<{ videoPath: string; videoData: VideoData } | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          paperIndex,
          interests,
          strengths,
        }),
      });
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Failed to generate video:", error);
      return null;
    }
  },

  // Get video file URL
  getVideoUrl: (videoPath: string): string => {
    if (videoPath.startsWith("http")) return videoPath;
    return `${API_BASE_URL}/videos/${videoPath}`;
  },
};
