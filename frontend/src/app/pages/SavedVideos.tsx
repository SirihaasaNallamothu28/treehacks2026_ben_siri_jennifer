import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { VideoCard } from "../components/VideoCard";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Brain, ArrowLeft } from "lucide-react";
import { getSavedVideos, SavedVideo } from "../../lib/savedVideos";

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

// saved videos come from localStorage (or defaults provided by library)
let initialSaved = getSavedVideos();

export function SavedVideos() {
  const navigate = useNavigate();
  const [selectedInterest, setSelectedInterest] = useState("All");
  const [selectedStrength, setSelectedStrength] = useState("All");
  const [savedVideosState, setSavedVideosState] = useState<SavedVideo[]>(initialSaved);

  useEffect(() => {
    const handler = () => setSavedVideosState(getSavedVideos());
    window.addEventListener("storage", handler);
    // refresh on mount
    setSavedVideosState(getSavedVideos());
    return () => window.removeEventListener("storage", handler);
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
          <p className="text-muted-foreground">You have {savedVideosState.length} saved videos</p>
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
          {savedVideosState.map((video) => (
            <VideoCard relevanceIcon={""} key={video.id} {...video} subtitle={video.subtitle ?? ""} showLinkOnHover={true} />
          ))}
        </div>
      </div>
    </div>
  );
}