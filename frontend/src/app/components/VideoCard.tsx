import { useState } from "react";
import { useNavigate } from "react-router";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { ExternalLink } from "lucide-react";

interface VideoCardProps {
  id: string;
  title: string;
  subtitle: string;
  relevanceBadge: string;
  relevanceIcon: string;
  studyType: string;
  sampleSize: string;
  year: string;
  metric: string;
  thumbnailUrl?: string;
  showLinkOnHover?: boolean;
}

export function VideoCard({
  id,
  title,
  subtitle,
  relevanceBadge,
  relevanceIcon,
  studyType,
  sampleSize,
  year,
  metric,
  thumbnailUrl,
  showLinkOnHover = false,
}: VideoCardProps) {
  const navigate = useNavigate();
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Card
      className="w-full overflow-hidden cursor-pointer transition-all hover:shadow-lg relative"
      onClick={() => navigate(`/video/${id}`)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Thumbnail */}
      <div className="w-full h-44 bg-gradient-to-br from-[#00b4d8]/20 to-[#0077b6]/20 flex items-center justify-center relative">
        {thumbnailUrl ? (
          <img src={thumbnailUrl} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="text-6xl">{relevanceIcon}</div>
        )}
        
        {/* Link button on hover */}
        {showLinkOnHover && isHovered && (
          <Button
            size="icon"
            variant="secondary"
            className="absolute top-2 right-2"
            onClick={(e) => {
              e.stopPropagation();
              window.open("https://example.com/paper", "_blank");
            }}
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-semibold mb-1 line-clamp-2">{title}</h3>
          <p className="text-sm text-muted-foreground line-clamp-1">{subtitle}</p>
        </div>

        {/* Relevance Badge */}
        <Badge variant="secondary" className="w-fit">
          {relevanceIcon} {relevanceBadge}
        </Badge>

        {/* Evidence Strip */}
        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
          <span className="px-2 py-1 bg-muted rounded">{studyType}</span>
          <span className="px-2 py-1 bg-muted rounded">{sampleSize}</span>
          <span className="px-2 py-1 bg-muted rounded">{year}</span>
          <span className="px-2 py-1 bg-muted rounded">{metric}</span>
        </div>
      </div>
    </Card>
  );
}