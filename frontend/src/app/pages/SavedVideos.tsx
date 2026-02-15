import { useState } from "react";
import { useNavigate } from "react-router";
import { VideoCard } from "../components/VideoCard";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Brain, ArrowLeft } from "lucide-react";

const FILTER_INTERESTS = [
  "All",
  "Medical imaging",
  "Drug discovery",
  "Clinical NLP", 
  "Genomics",
  "EHR / tabular",
];

const FILTER_STRENGTHS = [
  "All",
  "Computer vision",
  "LLMs",
  "Reinforcement learning",
  "Time series",
];

// Mock saved videos
const savedVideos = [
  {
    id: "1",
    title:
      "Deep Learning Models Outperform Radiologists in Detecting Lung Cancer",
    subtitle:
      "Diagnostic accuracy of deep learning for lung cancer detection...",
    relevanceBadge: "Uses CNNs",
    relevanceIcon: "🧠",
    studyType: "RCT",
    sampleSize: "n = 12,400",
    year: "2024",
    metric: "AUROC 0.94",
  },
  {
    id: "2",
    title:
      "Transformer Architecture Identifies Novel Drug Candidates for Alzheimer's",
    subtitle:
      "Machine learning approach to drug discovery in neurodegenerative...",
    relevanceBadge: "LLM-based",
    relevanceIcon: "🤖",
    studyType: "In silico",
    sampleSize: "n = 50k compounds",
    year: "2025",
    metric: "Hit rate 23%",
  },
  {
    id: "3",
    title:
      "Vision Transformers Achieve State-of-the-Art Diabetic Retinopathy Classification",
    subtitle:
      "Automated detection of diabetic retinopathy using modern vision...",
    relevanceBadge: "Uses CNNs",
    relevanceIcon: "🧠",
    studyType: "Retrospective",
    sampleSize: "n = 8,900",
    year: "2024",
    metric: "AUROC 0.97",
  },
  {
    id: "5",
    title: "Understanding Medical Image Analysis Basics",
    subtitle:
      "Introduction to computer vision in healthcare applications...",
    relevanceBadge: "Uses CNNs",
    relevanceIcon: "🧠",
    studyType: "Review",
    sampleSize: "87 studies",
    year: "2023",
    metric: "Systematic",
  },
  {
    id: "6",
    title:
      "Clinical Data Standards: HL7 FHIR for AI Researchers",
    subtitle:
      "Overview of healthcare data formats and interoperability...",
    relevanceBadge: "Tabular ML",
    relevanceIcon: "📊",
    studyType: "Tutorial",
    sampleSize: "N/A",
    year: "2024",
    metric: "Educational",
  },
  {
    id: "8",
    title: "Foundation Models for Medical Imaging Show Promise",
    subtitle:
      "Large-scale pre-training on medical images enables few-shot learning...",
    relevanceBadge: "Uses CNNs",
    relevanceIcon: "🧠",
    studyType: "Observational",
    sampleSize: "n = 100k images",
    year: "2026",
    metric: "AUROC 0.89",
  },
];

export function SavedVideos() {
  const navigate = useNavigate();
  const [selectedInterest, setSelectedInterest] =
    useState("All");
  const [selectedStrength, setSelectedStrength] =
    useState("All");

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-[#0077b6]" />
              <span className="text-xl font-semibold">
                Synapsis
              </span>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => navigate("/")}
          >
            Search
          </Button>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8 space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            Saved Videos
          </h1>
          <p className="text-muted-foreground">
            You have {savedVideos.length} saved videos
          </p>
        </div>

        {/* Filters */}
        <div className="space-y-4 bg-white p-6 rounded-lg shadow-sm">
          <div>
            <p className="text-sm font-medium mb-2">
              Filter by Interest
            </p>
            <div className="flex flex-wrap gap-2">
              {FILTER_INTERESTS.map((interest) => (
                <Badge
                  key={interest}
                  variant={
                    selectedInterest === interest
                      ? "default"
                      : "outline"
                  }
                  className="cursor-pointer px-4 py-2"
                  onClick={() => setSelectedInterest(interest)}
                >
                  {interest}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium mb-2">
              Filter by Strength
            </p>
            <div className="flex flex-wrap gap-2">
              {FILTER_STRENGTHS.map((strength) => (
                <Badge
                  key={strength}
                  variant={
                    selectedStrength === strength
                      ? "default"
                      : "outline"
                  }
                  className="cursor-pointer px-4 py-2"
                  onClick={() => setSelectedStrength(strength)}
                >
                  {strength}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Video Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {savedVideos.map((video) => (
            <VideoCard
              key={video.id}
              {...video}
              showLinkOnHover={true}
            />
          ))}
        </div>
      </div>
    </div>
  );
}