import { useNavigate, useParams } from "react-router";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import { Brain, ArrowLeft, Heart, Link, PlayCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

// Mock video data array for carousel
const allVideos = [
  {
    id: "1",
    title: "Deep Learning Models Outperform Radiologists in Detecting Lung Cancer",
    originalTitle: "Diagnostic accuracy of deep learning models for lung cancer detection in chest CT scans: A systematic review and meta-analysis",
    relevanceBadge: "Uses CNNs",
    description: "This video explains how modern convolutional neural networks achieve superior accuracy compared to human radiologists in detecting lung cancer from CT scans. The study demonstrates that CNNs can identify subtle patterns in medical imaging that may be missed by human observers, leading to earlier detection and better patient outcomes.",
    
    metadata: {
      citations: 247,
      year: 2024,
      journal: "Nature Medicine",
    },
    
    studyData: {
      datasetSize: "12,400 patients",
      trialSize: "Multi-center RCT",
      modality: "CT imaging",
      modelType: "ResNet-50 + Vision Transformer",
      evaluationMetric: "AUROC, Sensitivity, Specificity",
      studyType: "Randomized Controlled Trial",
    },
    
    results: {
      auroc: "0.94 (95% CI: 0.92-0.96)",
      pValue: "p < 0.001",
      sensitivity: "91.2%",
      specificity: "88.7%",
      improvement: "7.3% improvement over radiologist baseline",
    },
  },
  {
    id: "2",
    title: "Attention Mechanisms in Medical Image Analysis",
    originalTitle: "Vision transformers with attention mechanisms for medical image segmentation",
    relevanceBadge: "Uses CNNs",
    description: "Explore how attention mechanisms improve medical image analysis by focusing on relevant anatomical regions. This approach allows the model to learn which parts of an image are most important for diagnosis, similar to how radiologists focus their attention on specific areas of concern. The transformer architecture brings natural language processing advances to computer vision in healthcare.",
    
    metadata: {
      citations: 189,
      year: 2023,
      journal: "Medical Image Analysis",
    },
    
    studyData: {
      datasetSize: "8,200 patients",
      trialSize: "Single-center study",
      modality: "MRI imaging",
      modelType: "Vision Transformer",
      evaluationMetric: "Dice Score, IoU",
      studyType: "Retrospective Analysis",
    },
    
    results: {
      auroc: "0.91 (95% CI: 0.89-0.93)",
      pValue: "p < 0.01",
      sensitivity: "88.5%",
      specificity: "92.1%",
      improvement: "5.2% improvement over baseline",
    },
  },
  {
    id: "3",
    title: "Self-Supervised Learning for CT Scans",
    originalTitle: "Contrastive learning approaches for unlabeled medical imaging data",
    relevanceBadge: "Pretraining",
    description: "Learn how self-supervised pretraining techniques can improve model performance with limited labeled medical data. This research addresses one of the biggest challenges in medical AI: the scarcity of labeled training data. By leveraging large amounts of unlabeled medical images, models can learn useful representations before fine-tuning on specific tasks.",
    
    metadata: {
      citations: 312,
      year: 2024,
      journal: "Nature Biomedical Engineering",
    },
    
    studyData: {
      datasetSize: "25,000 patients",
      trialSize: "Multi-center study",
      modality: "CT imaging",
      modelType: "SimCLR + ResNet-101",
      evaluationMetric: "Transfer Learning Performance",
      studyType: "Validation Study",
    },
    
    results: {
      auroc: "0.89 (95% CI: 0.87-0.91)",
      pValue: "p < 0.001",
      sensitivity: "85.3%",
      specificity: "89.8%",
      improvement: "12.1% improvement with pretraining",
    },
  },
];

export function VideoPlayer() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [currentIndex, setCurrentIndex] = useState(0);

  const currentVideo = allVideos[currentIndex];
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < allVideos.length - 1;

  const goToPrevious = () => {
    if (hasPrevious) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const goToNext = () => {
    if (hasNext) {
      setCurrentIndex(currentIndex + 1);
    }
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
              disabled={!hasPrevious}
            >
              <ChevronLeft className="h-6 w-6" />
            </Button>

            {/* Carousel Cards Container */}
            <div className="relative w-full max-w-6xl flex items-start justify-center">
              {/* Previous Video (Left) - Partially visible */}
              {hasPrevious && (
                <div className="absolute left-0 top-0 z-0 transform -translate-x-32 scale-75 opacity-40">
                  <Card className="overflow-hidden w-[800px] pointer-events-none">
                    <div className="w-full aspect-video bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center">
                      <PlayCircle className="h-16 w-16 text-[#0077b6] opacity-70" />
                    </div>
                    <div className="p-6">
                      <h2 className="text-xl font-semibold line-clamp-2">{allVideos[currentIndex - 1].title}</h2>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{allVideos[currentIndex - 1].originalTitle}</p>
                    </div>
                  </Card>
                </div>
              )}

              {/* Current Video (Center) - Scrollable */}
              <div className="relative z-10 max-h-full overflow-y-auto">
                <Card className="overflow-hidden w-[800px] shadow-2xl">
                  <div className="w-full aspect-video bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center relative group sticky top-0 z-10">
                    <PlayCircle className="h-20 w-20 text-[#0077b6] opacity-70 group-hover:opacity-100 transition-opacity" />
                    
                    {/* Side Icons */}
                    <div className="absolute right-4 bottom-4 flex flex-col gap-2">
                      <Button size="icon" variant="secondary" className="rounded-full">
                        <Heart className="h-5 w-5" />
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
              {hasNext && (
                <div className="absolute right-0 top-0 z-0 transform translate-x-32 scale-75 opacity-40">
                  <Card className="overflow-hidden w-[800px] pointer-events-none">
                    <div className="w-full aspect-video bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center">
                      <PlayCircle className="h-16 w-16 text-[#0077b6] opacity-70" />
                    </div>
                    <div className="p-6">
                      <h2 className="text-xl font-semibold line-clamp-2">{allVideos[currentIndex + 1].title}</h2>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{allVideos[currentIndex + 1].originalTitle}</p>
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
              disabled={!hasNext}
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