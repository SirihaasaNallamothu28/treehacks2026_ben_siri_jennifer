import { useNavigate, useParams } from "react-router";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import { Brain, ArrowLeft, Heart, Link, PlayCircle, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { getVideoStatus, type VideoJob } from "../services/api";

// Video files from heygen_videos folder
const videoFiles = [
  { id: "1", videoPath: "/heygen_videos/obstructive_sleep_apnea.mp4" },
  { id: "2", videoPath: "/heygen_videos/zinc.mp4" },
  { id: "3", videoPath: "/heygen_videos/iv_lines.mp4" },
];

// Mock video data array for carousel
const allVideos = [
  {
    id: "1",
    title: "AI in Surgical Planning for Obstructive Sleep Apnea",
    originalTitle: "Artificial intelligence in surgical planning and outcome prediction for obstructive sleep apnea: emerging hype or the future standard?",
    relevanceBadge: "Predictive AI",
    description: "This video explores how AI can assist in surgical planning and outcome prediction for patients with obstructive sleep apnea. Deep learning models can enhance diagnostic accuracy, improve risk stratification, and predict surgical response better than traditional methods, potentially optimizing individualized care.",
    
    metadata: {
      citations: 0,
      year: 2025,
      journal: "Journal of Clinical Sleep Medicine",
    },
    
    studyData: {
      datasetSize: "2,100 patients across multiple centers",
      trialSize: "Retrospective + prospective validation",
      modality: "Polysomnography, wearable sleep monitoring",
      modelType: "Deep Learning Predictive Models",
      evaluationMetric: "AUROC, Accuracy, F1 Score",
      studyType: "Narrative Literature Review & Validation Study",
    },
    
    results: {
      auroc: "0.92 (estimated from literature synthesis)",
      pValue: "p < 0.01",
      sensitivity: "90.1%",
      specificity: "87.6%",
      improvement: "AI improved prediction of surgical response over traditional clinical scoring",
    },
  },
  {
    id: "2",
    title: "Zinc and Brain Regeneration: Therapeutic Insights",
    originalTitle: "The Impact of Zinc on Cellular Dynamics, Brain Function, and its Therapeutic Potential in Neuronal Regeneration.",
    relevanceBadge: "Neuroregeneration",
    description: "Discover the critical role of zinc in neuronal health and regeneration. Zinc modulates neurogenesis, synaptic plasticity, and neural repair pathways, with potential applications in neurodegenerative disease treatment and recovery after brain injury.",
    
    metadata: {
      citations: 0,
      year: 2026,
      journal: "Molecular Neurobiology",
    },
    
    studyData: {
      datasetSize: "Experimental in vitro & animal models",
      trialSize: "Controlled laboratory studies",
      modality: "Cell cultures, neural tissue assays",
      modelType: "Zinc supplementation & nanomaterials",
      evaluationMetric: "Neurite length, synaptic density, survival rate",
      studyType: "Experimental Therapeutic Study",
    },
    
    results: {
      auroc: "N/A (not diagnostic)",
      pValue: "p < 0.05",
      sensitivity: "N/A",
      specificity: "N/A",
      improvement: "Zinc supplementation enhanced neuronal survival and regeneration by ~18% over control conditions",
    },
  },
  {
    id: "3",
    title: "Chlorhexidine vs Povidone-Iodine in Catheter Infection Prevention",
    originalTitle: "Chlorhexidine vs Povidone-Iodine and Incidence of Catheter-Related Infections: A Systematic Review and Meta-Analysis.",
    relevanceBadge: "Infection Control",
    description: "This video reviews the effectiveness of different antiseptic agents for preventing catheter-related infections. Alcohol-based chlorhexidine formulations reduce bloodstream infections and colonization more effectively than povidone-iodine, guiding safer clinical practice.",
    
    metadata: {
      citations: 0,
      year: 2026,
      journal: "JAMA Network Open",
    },
    
    studyData: {
      datasetSize: "7,803 patients; 11,985 catheters",
      trialSize: "16 RCTs",
      modality: "Intravascular catheter insertion",
      modelType: "Network Meta-Analysis",
      evaluationMetric: "Relative Risk (RR) of CRBSI, colonization, local infection",
      studyType: "Systematic Review and Meta-Analysis",
    },
    
    results: {
      auroc: "N/A",
      pValue: "varies per study, pooled estimates used",
      sensitivity: "N/A",
      specificity: "N/A",
      improvement: "Alcohol-based CHG reduced CRBSI by ~30% compared with PVI",
    },
  },
];

export function VideoPlayer() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [videosWithGenerated, setVideosWithGenerated] = useState(allVideos);
  const [generatingVideo, setGeneratingVideo] = useState<VideoJob | null>(null);
  const [savedVideoIds, setSavedVideoIds] = useState<Set<string>>(() => {
    const saved = localStorage.getItem("savedVideos");
    return new Set(saved ? JSON.parse(saved) : []);
  });
  const currentVideo = videosWithGenerated[currentIndex];
  const len = videosWithGenerated.length;
  const canNavigate = len > 1;

  const handleSaveVideo = () => {
    const videoToSave = {
      id: currentVideo.id,
      title: currentVideo.title,
      originalTitle: currentVideo.originalTitle,
      relevanceBadge: currentVideo.relevanceBadge,
      description: currentVideo.description,
      metadata: currentVideo.metadata,
      videoPath: currentIndex < videoFiles.length ? videoFiles[currentIndex].videoPath : null,
    };

    // Get existing saved videos
    const saved = localStorage.getItem("savedVideosData");
    const savedVideos = saved ? JSON.parse(saved) : [];

    // Check if already saved
    const alreadySaved = savedVideos.some((v: any) => v.id === videoToSave.id);

    if (!alreadySaved) {
      savedVideos.push(videoToSave);
      localStorage.setItem("savedVideosData", JSON.stringify(savedVideos));

      // Update saved IDs
      const newSavedIds = new Set(savedVideoIds);
      newSavedIds.add(currentVideo.id);
      setSavedVideoIds(newSavedIds);
      localStorage.setItem("savedVideos", JSON.stringify([...newSavedIds]));
    }
  };

  // Poll for generating video on mount
  useEffect(() => {
    const jobId = localStorage.getItem("generatingJobId");
    if (!jobId) return;

    let isCancelled = false;

    const pollForVideo = async () => {
      try {
        const job = await getVideoStatus(jobId);
        if (isCancelled) return;

        setGeneratingVideo(job);

        // If completed, add to videos array
        if (job.status === "completed" && job.video_path && job.title) {
          // Create a new video object
          const newVideo = {
            id: `generated-${job.paper_index}`,
            title: job.title,
            originalTitle: job.title,
            relevanceBadge: "AI Generated",
            description: "This video was generated based on your interests using AI analysis of recent research papers.",
            metadata: job.metadata || {
              citations: 0,
              year: "2026",
              journal: "Generated",
            },
            studyData: {
              datasetSize: "Generated from paper analysis",
              trialSize: "N/A",
              modality: "AI-generated explainer",
              modelType: "HeyGen AI Avatar",
              evaluationMetric: "N/A",
              studyType: "Research Summary",
            },
            results: {
              auroc: "N/A",
              pValue: "N/A",
              sensitivity: "N/A",
              specificity: "N/A",
              improvement: "Video generated from cutting-edge research",
            },
          };

          // Add to videos array if not already there
          setVideosWithGenerated((prev) => {
            const exists = prev.find((v) => v.id === newVideo.id);
            if (!exists) {
              return [...prev, newVideo];
            }
            return prev;
          });

          // Add to videoFiles array with backend URL
          const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
          const newVideoFile = {
            id: newVideo.id,
            videoPath: `${apiUrl}/${job.video_path}`,
          };

          // Check if already in videoFiles
          const existsInFiles = videoFiles.find((v) => v.id === newVideo.id);
          if (!existsInFiles) {
            videoFiles.push(newVideoFile);
          }

          // Clear the job ID
          localStorage.removeItem("generatingJobId");
        } else if (job.status === "failed") {
          console.error("Video generation failed:", job.error);
          localStorage.removeItem("generatingJobId");
        } else {
          // Still generating, poll again in 3 seconds
          setTimeout(pollForVideo, 3000);
        }
      } catch (error) {
        console.error("Error polling video status:", error);
        if (!isCancelled) {
          setTimeout(pollForVideo, 3000);
        }
      }
    };

    // Add a loading placeholder video immediately
    const loadingVideo = {
      id: "loading",
      title: "Generating your personalized video...",
      originalTitle: "AI is analyzing the research paper and creating your video",
      relevanceBadge: "Generating",
      description: "Please wait while we analyze the research paper and generate a personalized video for you. This may take a few minutes.",
      metadata: {
        citations: 0,
        year: "2026",
        journal: "Generating...",
      },
      studyData: {
        datasetSize: "Analyzing...",
        trialSize: "Generating...",
        modality: "AI Video Generation",
        modelType: "HeyGen AI Avatar",
        evaluationMetric: "In Progress",
        studyType: "Research Summary",
      },
      results: {
        auroc: "Pending",
        pValue: "Pending",
        sensitivity: "Pending",
        specificity: "Pending",
        improvement: "Video generation in progress...",
      },
    };

    // Add loading video to the array
    setVideosWithGenerated((prev) => {
      const hasLoading = prev.find((v) => v.id === "loading");
      if (!hasLoading) {
        return [...prev, loadingVideo];
      }
      return prev;
    });

    // Start polling
    pollForVideo();

    return () => {
      isCancelled = true;
    };
  }, []);


  const prevIndex = (currentIndex - 1 + len) % len;
  const nextIndex = (currentIndex + 1) % len;

  const goToPrevious = () => {
    if (!canNavigate) return;
    setCurrentIndex((i) => (i - 1 + len) % len);
  };

  const goToNext = () => {
    if (!canNavigate) return;
    setCurrentIndex((i) => (i + 1) % len);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/")}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-[#0077b6]" />
              <span className="text-xl font-semibold">Synapsis</span>
            </div>
          </div>
          <Button variant="outline" onClick={() => navigate("/saved")}>
            Saved
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Carousel Container - Fixed height viewport */}
        <div className="relative mb-8 h-screen overflow-hidden">
          <div className="flex items-start justify-center h-full pt-8">
            {/* Left Arrow Button */}
            <Button
              size="icon"
              variant="secondary"
              className="rounded-full shadow-lg flex-shrink-0 z-20 mr-4 sticky top-1/2 -translate-y-1/2"
              onClick={goToPrevious}
              disabled={!canNavigate}
            >
              <ChevronLeft className="h-6 w-6" />
            </Button>

            {/* Carousel Cards Container */}
            <div className="relative w-full max-w-6xl flex items-start justify-center">
              {/* Previous Video (Left) - Partially visible */}
              {canNavigate && (
                <div className="absolute left-0 top-0 z-0 transform -translate-x-32 scale-75 opacity-40">
                  <Card className="overflow-hidden w-[800px] pointer-events-none">
                    <div className="w-full aspect-video bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center">
                      <PlayCircle className="h-16 w-16 text-[#0077b6] opacity-70" />
                    </div>
                    <div className="p-6">
                      <h2 className="text-xl font-semibold line-clamp-2">{allVideos[prevIndex].title}</h2>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{allVideos[prevIndex].originalTitle}</p>
                    </div>
                  </Card>
                </div>
              )}

              {/* Current Video (Center) - Scrollable */}
              <div className="relative z-10 max-h-full overflow-y-auto">
                <Card className="overflow-hidden w-[800px] shadow-2xl">
                  <div className="w-full aspect-video bg-black relative group sticky top-0 z-10">
                      {currentVideo.id === "loading" ? (
                      <div className="flex flex-col items-center justify-center h-full bg-gradient-to-br from-[#0077b6]/20 to-[#00b4d8]/20">
                        <Loader2 className="h-16 w-16 text-[#0077b6] animate-spin mb-4" />
                        <p className="text-white text-lg font-medium">
                          {generatingVideo?.message || "Generating video..."}
                        </p>
                      </div>
                    ) : currentIndex < videoFiles.length ? (
                      <video
                        key={videoFiles[currentIndex].videoPath}
                        width="100%"
                        height="100%"
                        controls
                        className="w-full h-full object-cover"
                      >
                        <source src={videoFiles[currentIndex].videoPath} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <PlayCircle className="h-20 w-20 text-[#0077b6] opacity-70" />
                      </div>
                    )}
                    
                    {/* Side Icons */}
                    <div className="absolute right-4 bottom-4 flex flex-col gap-2">
                      <Button
                        size="icon"
                        variant="secondary"
                        className="rounded-full"
                        onClick={handleSaveVideo}
                      >
                        <Heart
                          className={`h-5 w-5 ${savedVideoIds.has(currentVideo.id) ? "fill-red-500 text-red-500" : ""}`}
                        />
                      </Button>
                      <Button
                        size="icon"
                        variant="secondary"
                        className="rounded-full"
                        onClick={() => window.open("https://example.com/paper", "_blank")}
                      >
                        <Link className="h-5 w-5" />
                      </Button>
                    </div>
                  </div>

                  <div className="p-6 space-y-4">
                    <div>
                      <h1 className="text-2xl font-semibold mb-2">{currentVideo.title}</h1>
                      <p className="text-sm text-muted-foreground">{currentVideo.originalTitle}</p>
                    </div>
                    
                    <div className="flex gap-2">
                      <Badge>{currentVideo.relevanceBadge}</Badge>
                    </div>

                    <p className="text-muted-foreground">{currentVideo.description}</p>
                  </div>
                </Card>
              </div>

              {/* Next Video (Right) - Partially visible */}
              {canNavigate && (
                <div className="absolute right-0 top-0 z-0 transform translate-x-32 scale-75 opacity-40">
                  <Card className="overflow-hidden w-[800px] pointer-events-none">
                    <div className="w-full aspect-video bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center">
                      <PlayCircle className="h-16 w-16 text-[#0077b6] opacity-70" />
                    </div>
                    <div className="p-6">
                      <h2 className="text-xl font-semibold line-clamp-2">{allVideos[nextIndex].title}</h2>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{allVideos[nextIndex].originalTitle}</p>
                    </div>
                  </Card>
                </div>
              )}
            </div>

            {/* Right Arrow Button */}
            <Button
              size="icon"
              variant="secondary"
              className="rounded-full shadow-lg flex-shrink-0 z-20 ml-4 sticky top-1/2 -translate-y-1/2"
              onClick={goToNext}
              disabled={!canNavigate}
            >
              <ChevronRight className="h-6 w-6" />
            </Button>
          </div>
        </div>

        {/* Metadata Sections Below Carousel */}
        <div className="max-w-4xl mx-auto mt-8">
          <Card className="p-6 space-y-6">
            {/* Metadata */}
            <div>
              <h3 className="font-semibold mb-3 text-lg">Metadata</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Citations:</strong> {currentVideo.metadata.citations}</p>
                <p><strong>Year:</strong> {currentVideo.metadata.year}</p>
                <p><strong>Journal:</strong> {currentVideo.metadata.journal}</p>
              </div>
            </div>

            <Separator />

            {/* Study Design (renamed from Study Data) */}
            <div>
              <h3 className="font-semibold mb-3 text-lg">Study Design</h3>
              <div className="space-y-1 text-sm">
                <p><strong>Dataset Size:</strong> {currentVideo.studyData.datasetSize}</p>
                <p><strong>Trial:</strong> {currentVideo.studyData.trialSize}</p>
                <p><strong>Modality:</strong> {currentVideo.studyData.modality}</p>
                <p><strong>Model:</strong> {currentVideo.studyData.modelType}</p>
                <p><strong>Metrics:</strong> {currentVideo.studyData.evaluationMetric}</p>
                <p><strong>Type:</strong> {currentVideo.studyData.studyType}</p>
              </div>
            </div>

            <Separator />

            {/* Results */}
            <div>
              <h3 className="font-semibold mb-3 text-lg">Results</h3>
              <div className="space-y-1 text-sm">
                <p><strong>AUROC:</strong> {currentVideo.results.auroc}</p>
                <p><strong>p-value:</strong> {currentVideo.results.pValue}</p>
                <p><strong>Sensitivity:</strong> {currentVideo.results.sensitivity}</p>
                <p><strong>Specificity:</strong> {currentVideo.results.specificity}</p>
                <p className="text-green-600 font-medium mt-2">{currentVideo.results.improvement}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}