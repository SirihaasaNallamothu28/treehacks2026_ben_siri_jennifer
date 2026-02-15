import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { SearchBarChips } from "../components/SearchBarChips";
import { Brain } from "lucide-react";

export function Home() {
  const navigate = useNavigate();
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedStrengths, setSelectedStrengths] = useState<string[]>([]);

  const handleSearch = () => {
    // Save to localStorage with formatted string
    const userProfile = `User interested in healthcare: user interests in ${selectedInterests.join(", ")}. User strengths in ${selectedStrengths.join(", ")}.`;
    localStorage.setItem("userProfile", userProfile);
    console.log("Saved:", userProfile);
    
    // Show loading screen for 8 seconds, then navigate
    setIsLoading(true);
    setSecondsLeft(8);
    const t = setInterval(() => {
      setSecondsLeft((s) => s - 1);
    }, 1000);
    setTimeout(() => {
      clearInterval(t);
      setIsLoading(false);
      navigate("/video/1");
    }, 8000);
  };

  const [isLoading, setIsLoading] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(8);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#00b4d8]/10 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-[#0077b6]" />
            <span className="text-xl font-semibold">Synapsis</span>
          </div>
          <Button variant="outline" onClick={() => navigate("/saved")}>
            Saved
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 max-w-4xl">
        {isLoading && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/95">
            <div className="text-center">
              <div className="mb-4 text-2xl font-semibold">Preparing your recommendations...</div>
              <div className="mb-4 text-sm text-muted-foreground">Please wait — loading ({secondsLeft}s)</div>
              <div className="w-64 h-2 bg-gray-200 rounded overflow-hidden mx-auto">
                <div
                  className="h-full bg-[#0077b6]"
                  style={{ width: `${((8 - Math.max(0, secondsLeft)) / 8) * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}
        <div className="text-center space-y-6 mb-16">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#0077b6] to-[#00b4d8] bg-clip-text text-transparent">
            Synapsing the Gap Between AI and Healthcare
          </h1>
          <p className="text-xl text-muted-foreground">
            Get personalized video recommendations and discover your niche in medical AI research
          </p>
        </div>

        {/* Selection Form */}
        <div className="space-y-12 bg-white rounded-lg shadow-lg p-8">
          <SearchBarChips
            label="What are your interests in AI?"
            placeholder="Medical imaging, Drug discovery, Clinical NLP, Genomics..."
            onSelectionChange={setSelectedInterests}
          />

          <SearchBarChips
            label="What are your interests in Healthcare?"
            placeholder="Computer vision, Diffusion modeling, LLMs, Reinforcement learning..."
            onSelectionChange={setSelectedStrengths}
          />

          <div className="flex justify-center pt-4">
            <Button
              size="lg"
              onClick={handleSearch}
              className="px-8"
            >
              Discover Research
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}