import { useState, useEffect } from "react";
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

export function SavedVideos() {
  const navigate = useNavigate();
  const [selectedInterest, setSelectedInterest] = useState("All");
  const [selectedStrength, setSelectedStrength] = useState("All");
  const [savedVideos, setSavedVideos] = useState<any[]>([]);

  // Load saved videos from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("savedVideosData");
    if (saved) {
      const videos = JSON.parse(saved);
      // Convert to the format VideoCard expects
      const formatted = videos.map((v: any) => ({
        id: v.id,
        title: v.title,
        subtitle: v.originalTitle,
        relevanceBadge: v.relevanceBadge,
        relevanceIcon: "🎬",
        studyType: "Research",
        sampleSize: v.metadata?.citations ? `${v.metadata.citations} citations` : "N/A",
        year: v.metadata?.year?.toString() || "N/A",
        metric: "Saved",
      }));
      setSavedVideos(formatted);
    }
  }, []);

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
            You have {savedVideos.length} saved video{savedVideos.length !== 1 ? "s" : ""}
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
        {savedVideos.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-lg mb-4">No saved videos yet</p>
            <p className="text-sm text-muted-foreground mb-6">
              Click the heart icon on any video to save it here
            </p>
            <Button onClick={() => navigate("/")}>
              Discover Videos
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {savedVideos.map((video) => (
              <VideoCard
                key={video.id}
                {...video}
                showLinkOnHover={true}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}