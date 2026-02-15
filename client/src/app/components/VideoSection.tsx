import { ReactNode } from "react";
import { ScrollArea, ScrollBar } from "./ui/scroll-area";

interface VideoSectionProps {
  title: string;
  children: ReactNode;
}

export function VideoSection({ title, children }: VideoSectionProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">{title}</h2>
      <div className="border-t pt-4">
        <ScrollArea className="w-full whitespace-nowrap">
          <div className="flex gap-4 pb-4">
            {children}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>
    </div>
  );
}
