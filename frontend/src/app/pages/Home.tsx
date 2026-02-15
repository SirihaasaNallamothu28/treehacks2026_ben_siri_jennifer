import { useState } from "react";
import { useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { SearchBarChips } from "../components/SearchBarChips";
import { Brain } from "lucide-react";

export function Home() {
  const navigate = useNavigate();
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedStrengths, setSelectedStrengths] = useState<string[]>([]);

  const handleSearch = () => {
    if (selectedInterests.length > 0 || selectedStrengths.length > 0) {
      navigate("/video/1");
    }
  };

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
            label="What are your interests?"
            placeholder="Medical imaging, Drug discovery, Clinical NLP, Genomics..."
            onSelectionChange={setSelectedInterests}
          />

          <SearchBarChips
            label="What are your strengths?"
            placeholder="Computer vision, Diffusion modeling, LLMs, Reinforcement learning..."
            onSelectionChange={setSelectedStrengths}
          />

          <div className="flex justify-center pt-4">
            <Button
              size="lg"
              onClick={handleSearch}
              disabled={selectedInterests.length === 0 && selectedStrengths.length === 0}
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