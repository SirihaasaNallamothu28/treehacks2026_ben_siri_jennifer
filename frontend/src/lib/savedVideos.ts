export type SavedVideo = {
  id: string;
  title: string;
  subtitle?: string;
  relevanceBadge?: string;
  studyType?: string;
  sampleSize?: string;
  year?: string | number;
  metric?: string;
};

const STORAGE_KEY = "syn_saved_videos";

export const DEFAULT_SAVED_VIDEOS: SavedVideo[] = [
  {
    id: "1",
    title: "Deep Learning Models Outperform Radiologists in Detecting Lung Cancer",
    subtitle: "Diagnostic accuracy of deep learning for lung cancer detection...",
    relevanceBadge: "Uses CNNs",
    studyType: "RCT",
    sampleSize: "n = 12,400",
    year: "2024",
    metric: "AUROC 0.94",
  },
  {
    id: "2",
    title: "Transformer Architecture Identifies Novel Drug Candidates for Alzheimer's",
    subtitle: "Machine learning approach to drug discovery in neurodegenerative...",
    relevanceBadge: "LLM-based",
    studyType: "In silico",
    sampleSize: "n = 50k compounds",
    year: "2025",
    metric: "Hit rate 23%",
  },
  {
    id: "3",
    title: "Vision Transformers Achieve State-of-the-Art Diabetic Retinopathy Classification",
    subtitle: "Automated detection of diabetic retinopathy using modern vision...",
    relevanceBadge: "Uses CNNs",
    studyType: "Retrospective",
    sampleSize: "n = 8,900",
    year: "2024",
    metric: "AUROC 0.97",
  },
  {
    id: "5",
    title: "Understanding Medical Image Analysis Basics",
    subtitle: "Introduction to computer vision in healthcare applications...",
    relevanceBadge: "Uses CNNs",
    studyType: "Review",
    sampleSize: "87 studies",
    year: "2023",
    metric: "Systematic",
  },
  {
    id: "6",
    title: "Clinical Data Standards: HL7 FHIR for AI Researchers",
    subtitle: "Overview of healthcare data formats and interoperability...",
    relevanceBadge: "Tabular ML",
    studyType: "Tutorial",
    sampleSize: "N/A",
    year: "2024",
    metric: "Educational",
  },
  {
    id: "8",
    title: "Foundation Models for Medical Imaging Show Promise",
    subtitle: "Large-scale pre-training on medical images enables few-shot learning...",
    relevanceBadge: "Uses CNNs",
    studyType: "Observational",
    sampleSize: "n = 100k images",
    year: "2026",
    metric: "AUROC 0.89",
  },
];

export function getSavedVideos(): SavedVideo[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_SAVED_VIDEOS.slice();
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return DEFAULT_SAVED_VIDEOS.slice();
    return parsed;
  } catch (e) {
    return DEFAULT_SAVED_VIDEOS.slice();
  }
}

export function addSavedVideo(v: SavedVideo) {
  const list = getSavedVideos();
  const exists = list.some((x) => x.title === v.title);
  if (exists) return;
  list.unshift(v);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

export function removeSavedVideo(id: string) {
  const list = getSavedVideos().filter((x) => x.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}
